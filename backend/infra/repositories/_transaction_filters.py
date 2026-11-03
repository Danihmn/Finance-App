from sqlalchemy import Select, func, or_

from domain.read_models import TransactionFilters
from infra.database.models import BankAccounts, PluggyItems, Transactions

# Pluggy's `category` field is returned in English (see "Transaction Categorization" guide).
# Categorization is a premium feature: with it off, `category` is NULL and nothing is excluded.
CREDIT_CARD_PAYMENT_CATEGORY = "Credit card payment"
SAME_PERSON_TRANSFER_PREFIX = (
    "Same person transfer"  # also matches "... - PIX", "... - TED"
)


def join_owner(stmt: Select) -> Select:
    """transactions -> bank_accounts -> pluggy_items (the owner is pluggy_items.user_id)."""
    return stmt.join(
        BankAccounts, Transactions.bank_account_id == BankAccounts.id
    ).join(PluggyItems, BankAccounts.pluggy_item_id == PluggyItems.id)


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def apply_filters(stmt: Select, filters: TransactionFilters) -> Select:
    """Adds the WHERE clauses. The statement must already be joined with join_owner()."""
    stmt = stmt.where(Transactions.deleted_at.is_(None))
    if filters.user_id is not None:
        stmt = stmt.where(PluggyItems.user_id == filters.user_id)
    if filters.bank_account_id is not None:
        stmt = stmt.where(Transactions.bank_account_id == filters.bank_account_id)
    if filters.date_from is not None:
        stmt = stmt.where(Transactions.date >= filters.date_from)
    if filters.date_to is not None:
        stmt = stmt.where(Transactions.date < filters.date_to)
    if filters.type is not None:
        stmt = stmt.where(Transactions.type == filters.type)
    if filters.status is not None:
        stmt = stmt.where(Transactions.status == filters.status)
    if filters.category is not None:
        stmt = stmt.where(Transactions.category == filters.category)
    if filters.search:
        pattern = f"%{_escape_like(filters.search)}%"
        stmt = stmt.where(Transactions.description.ilike(pattern, escape="\\"))
    if filters.min_amount is not None:
        stmt = stmt.where(func.abs(Transactions.amount) >= filters.min_amount)
    if filters.max_amount is not None:
        stmt = stmt.where(func.abs(Transactions.amount) <= filters.max_amount)
    if filters.exclude_internal:
        internal = or_(
            Transactions.category == CREDIT_CARD_PAYMENT_CATEGORY,
            Transactions.category.like(f"{SAME_PERSON_TRANSFER_PREFIX}%"),
        )
        # A NULL category makes `NOT internal` NULL, which would drop the row: keep it explicitly
        stmt = stmt.where(or_(Transactions.category.is_(None), ~internal))
    return stmt
