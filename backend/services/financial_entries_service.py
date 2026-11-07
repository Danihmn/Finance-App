import datetime
import uuid

from sqlalchemy.orm import Session

from domain.entities import FinancialEntry
from infra.repositories import financial_entries_repository
from services._mappers import to_entity, to_values
from services.exceptions import translate_repository_errors


@translate_repository_errors
def get_financial_entry_by_id(session: Session, entry_id: uuid.UUID) -> FinancialEntry:
    entry = financial_entries_repository.get_financial_entry_by_id(session, entry_id)
    return to_entity(FinancialEntry, entry)


@translate_repository_errors
def list_financial_entries_by_user(
    session: Session,
    user_id: uuid.UUID,
    reference_month_from: datetime.date | None = None,
    reference_month_to: datetime.date | None = None,
    status: str | None = None,
    bank_account_id: uuid.UUID | None = None,
) -> list[FinancialEntry]:
    entries = financial_entries_repository.list_financial_entries_by_user(
        session,
        user_id,
        reference_month_from,
        reference_month_to,
        status,
        bank_account_id,
    )
    return [to_entity(FinancialEntry, e) for e in entries]


@translate_repository_errors
def create_financial_entry(session: Session, entry: FinancialEntry) -> FinancialEntry:
    created = financial_entries_repository.create_financial_entry(
        session, to_values(entry)
    )
    return to_entity(FinancialEntry, created)


@translate_repository_errors
def update_financial_entry(
    session: Session, entry_id: uuid.UUID, entry: FinancialEntry
) -> FinancialEntry:
    """Overwrites every column with the entity's values (id and created_at are kept)."""
    values = {
        k: v for k, v in to_values(entry).items() if k not in ("id", "created_at")
    }
    updated = financial_entries_repository.update_financial_entry(
        session, entry_id, values
    )
    return to_entity(FinancialEntry, updated)


@translate_repository_errors
def mark_financial_entries_status(
    session: Session, ids: list[uuid.UUID], status: str
) -> None:
    financial_entries_repository.update_financial_entries_status(session, ids, status)


@translate_repository_errors
def mark_financial_entry_deleted(
    session: Session, entry_id: uuid.UUID
) -> FinancialEntry:
    entry = financial_entries_repository.soft_delete_financial_entry(session, entry_id)
    return to_entity(FinancialEntry, entry)
