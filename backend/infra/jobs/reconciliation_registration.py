import datetime
import uuid

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from domain.entities import FinancialEntry, Transaction
from domain.read_models import TransactionFilters
from infra.database.session import get_session
from services.financial_entries_service import list_financial_entries_by_user
from services.transactions_service import search_transactions

_MONTHS_WINDOW = 2
_TRANSACTIONS_PAGE_SIZE = 200


def _load_transactions(session: Session, user_id: uuid.UUID) -> list[Transaction]:
    """Every POSTED transaction of the user in the last months (all pages)."""
    filters = TransactionFilters(
        user_id=user_id,
        date_from=datetime.datetime.now(datetime.UTC)
        - relativedelta(months=_MONTHS_WINDOW),
        status="POSTED",
    )

    transactions: list[Transaction] = []
    offset = 0
    while True:
        page, total = search_transactions(
            session, filters, limit=_TRANSACTIONS_PAGE_SIZE, offset=offset
        )
        transactions.extend(item.transaction for item in page)

        offset += _TRANSACTIONS_PAGE_SIZE
        if not page or offset >= total:
            break

    return transactions


def _load_financial_entries(
    session: Session, user_id: uuid.UUID
) -> list[FinancialEntry]:
    """Entries still waiting for a bank transaction, from the first day of the window's month."""
    first_month = datetime.date.today().replace(day=1) - relativedelta(
        months=_MONTHS_WINDOW
    )
    return list_financial_entries_by_user(
        session,
        user_id,
        reference_month_from=first_month,
        status="PLANNED",
    )


def reconciliate_financial_entries(user_id: uuid.UUID) -> None:
    """
    Reconciliate financial entries in the system.

    It compares the stored transactions with the actual financial records
    and identifies any date and amount discrepancies...
    If found any discrepancies, it won't do nothing.
    """
    with get_session() as session:
        transactions = _load_transactions(session, user_id)
        entries = _load_financial_entries(session, user_id)

        # TODO: matching logic goes here. When it writes anything, it also needs
        # session.commit() and error handling (see transaction_launcher.py)
        _ = transactions, entries
