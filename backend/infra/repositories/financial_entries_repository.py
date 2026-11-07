import datetime
import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from infra.database.models import FinancialEntries
from infra.repositories.exceptions import RecordNotFoundError, translate_db_errors

# Ids per UPDATE statement.
_CHUNK_SIZE = 500


@translate_db_errors("financial_entries")
def get_financial_entry_by_id(
    session: Session, entry_id: uuid.UUID
) -> FinancialEntries:
    entry = session.get(FinancialEntries, entry_id)
    if entry is None:
        raise RecordNotFoundError("financial_entries", "get_financial_entry_by_id")
    return entry


@translate_db_errors("financial_entries")
def list_financial_entries_by_user(
    session: Session,
    user_id: uuid.UUID,
    reference_month_from: datetime.date | None = None,  # inclusive
    reference_month_to: datetime.date | None = None,  # exclusive
    status: str | None = None,
    bank_account_id: uuid.UUID | None = None,
) -> list[FinancialEntries]:
    """Entries that were not soft deleted, with no pagination (few rows per user)."""
    stmt = (
        select(FinancialEntries)
        .where(FinancialEntries.user_id == user_id)
        .where(FinancialEntries.deleted_at.is_(None))
    )
    if reference_month_from is not None:
        stmt = stmt.where(FinancialEntries.reference_month >= reference_month_from)
    if reference_month_to is not None:
        stmt = stmt.where(FinancialEntries.reference_month < reference_month_to)
    if status is not None:
        stmt = stmt.where(FinancialEntries.status == status)
    if bank_account_id is not None:
        stmt = stmt.where(FinancialEntries.bank_account_id == bank_account_id)
    stmt = stmt.order_by(
        FinancialEntries.reference_month,
        FinancialEntries.due_date,
        FinancialEntries.id,
    )
    return list(session.scalars(stmt).all())


@translate_db_errors("financial_entries")
def create_financial_entry(
    session: Session, values: dict[str, Any]
) -> FinancialEntries:
    """`values` uses FinancialEntries column names."""
    entry = FinancialEntries(**values)
    session.add(entry)
    session.flush()
    return entry


@translate_db_errors("financial_entries")
def update_financial_entry(
    session: Session, entry_id: uuid.UUID, values: dict[str, Any]
) -> FinancialEntries:
    """Sets only the given columns. `values` uses FinancialEntries column names."""
    entry = get_financial_entry_by_id(session, entry_id)
    for key, value in values.items():
        setattr(entry, key, value)
    entry.updated_at = datetime.datetime.now(datetime.UTC)
    session.flush()
    return entry


@translate_db_errors("financial_entries")
def update_financial_entries_status(
    session: Session, ids: list[uuid.UUID], status: str
) -> None:
    now = datetime.datetime.now(datetime.UTC)
    for start in range(0, len(ids), _CHUNK_SIZE):
        chunk = ids[start : start + _CHUNK_SIZE]
        session.execute(
            update(FinancialEntries)
            .where(FinancialEntries.id.in_(chunk))
            .values(status=status, updated_at=now)
        )


@translate_db_errors("financial_entries")
def soft_delete_financial_entry(
    session: Session, entry_id: uuid.UUID
) -> FinancialEntries:
    entry = get_financial_entry_by_id(session, entry_id)
    now = datetime.datetime.now(datetime.UTC)
    entry.deleted_at = now
    entry.updated_at = now
    session.flush()
    return entry
