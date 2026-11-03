import decimal
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from domain.read_models import (
    CategoryTotal,
    CurrencyTotals,
    SpendingSummary,
    TransactionFilters,
    UserTotal,
)
from infra.database.models import BankAccounts, PluggyItems, Transactions, Users
from infra.repositories._transaction_filters import apply_filters, join_owner
from infra.repositories.exceptions import translate_db_errors

# Pluggy does not use the same sign for every account type (a card charge is positive, a bank
# debit is negative), so the direction comes from `type` and the value from abs(amount).
_DEBIT = "DEBIT"
_CREDIT = "CREDIT"
_BANK = "BANK"

_ZERO = decimal.Decimal("0.00")


@translate_db_errors("transactions")
def get_spending_summary(
    session: Session, filters: TransactionFilters
) -> SpendingSummary:
    """Totals per currency, and spending per category and per user.

    spent    = every DEBIT.
    received = CREDIT on BANK accounts only. A CREDIT on a card is a bill payment or a refund,
               not income.
    Currencies are never mixed. Filters decide the period, the status and the exclusions.
    """
    amount = func.abs(Transactions.amount)

    # ---- totals
    totals_stmt = apply_filters(
        join_owner(
            select(
                Transactions.currency_code,
                Transactions.type,
                BankAccounts.type,
                func.sum(amount),
                func.count(Transactions.id),
            )
        ),
        filters,
    ).group_by(Transactions.currency_code, Transactions.type, BankAccounts.type)

    spent: dict[str, decimal.Decimal] = defaultdict(lambda: _ZERO)
    received: dict[str, decimal.Decimal] = defaultdict(lambda: _ZERO)
    counted: dict[str, int] = defaultdict(int)
    for currency, tx_type, account_type, total, count in session.execute(totals_stmt):
        if tx_type == _DEBIT:
            spent[currency] += total
            counted[currency] += count
        elif tx_type == _CREDIT and account_type == _BANK:
            received[currency] += total
            counted[currency] += count
    currencies = sorted(set(spent) | set(received))

    # ---- spending per category
    category_stmt = (
        apply_filters(
            join_owner(
                select(
                    Transactions.currency_code,
                    Transactions.category,
                    func.sum(amount).label("total"),
                    func.count(Transactions.id),
                )
            ),
            filters,
        )
        .where(Transactions.type == _DEBIT)
        .group_by(Transactions.currency_code, Transactions.category)
        .order_by(Transactions.currency_code, func.sum(amount).desc())
    )

    # ---- spending per user
    user_stmt = (
        apply_filters(
            join_owner(
                select(
                    Transactions.currency_code,
                    PluggyItems.user_id,
                    Users.first_name,
                    func.sum(amount).label("total"),
                    func.count(Transactions.id),
                )
            ).join(Users, PluggyItems.user_id == Users.id),
            filters,
        )
        .where(Transactions.type == _DEBIT)
        .group_by(Transactions.currency_code, PluggyItems.user_id, Users.first_name)
        .order_by(Transactions.currency_code, func.sum(amount).desc())
    )

    return SpendingSummary(
        totals=[
            CurrencyTotals(
                currency_code=currency,
                total_spent=spent[currency],
                total_received=received[currency],
                transaction_count=counted[currency],
            )
            for currency in currencies
        ],
        by_category=[
            CategoryTotal(
                currency_code=currency,
                category=category,
                total_spent=total,
                transaction_count=count,
            )
            for currency, category, total, count in session.execute(category_stmt)
        ],
        by_user=[
            UserTotal(
                currency_code=currency,
                user_id=user_id,
                first_name=first_name,
                total_spent=total,
                transaction_count=count,
            )
            for currency, user_id, first_name, total, count in session.execute(
                user_stmt
            )
        ],
    )
