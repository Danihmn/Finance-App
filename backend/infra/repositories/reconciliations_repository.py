import datetime
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.database.models import Reconciliations
from infra.repositories.exceptions import RecordNotFoundError, translate_db_errors

# Ids per IN clause.
_CHUNK_SIZE = 500


@translate_db_errors("reconciliations")
def get_reconciliation_by_id(
    session: Session, reconciliation_id: uuid.UUID
) -> Reconciliations:
    reconciliation = session.get(Reconciliations, reconciliation_id)
    if reconciliation is None:
        raise RecordNotFoundError("reconciliations", "get_reconciliation_by_id")
    return reconciliation


@translate_db_errors("reconciliations")
def create_reconciliation(
    session: Session, values: dict[str, Any]
) -> Reconciliations:
    """`values` uses Reconciliations column names.

    An active reconciliation of the same entry and transaction raises DuplicateRecordError.
    """
    reconciliation = Reconciliations(**values)
    session.add(reconciliation)
    session.flush()
    return reconciliation


@translate_db_errors("reconciliations")
def list_reconciliations_by_entries(
    session: Session, entry_ids: list[uuid.UUID]
) -> list[Reconciliations]:
    """Active reconciliations (not soft deleted) of the given financial entries."""
    found: list[Reconciliations] = []
    for start in range(0, len(entry_ids), _CHUNK_SIZE):
        chunk = entry_ids[start : start + _CHUNK_SIZE]
        stmt = (
            select(Reconciliations)
            .where(Reconciliations.financial_entry_id.in_(chunk))
            .where(Reconciliations.deleted_at.is_(None))
            .order_by(Reconciliations.created_at, Reconciliations.id)
        )
        found.extend(session.scalars(stmt).all())
    return found


@translate_db_errors("reconciliations")
def list_reconciliations_by_transactions(
    session: Session, transaction_ids: list[uuid.UUID]
) -> list[Reconciliations]:
    """Active reconciliations (not soft deleted) of the given transactions."""
    found: list[Reconciliations] = []
    for start in range(0, len(transaction_ids), _CHUNK_SIZE):
        chunk = transaction_ids[start : start + _CHUNK_SIZE]
        stmt = (
            select(Reconciliations)
            .where(Reconciliations.transaction_id.in_(chunk))
            .where(Reconciliations.deleted_at.is_(None))
            .order_by(Reconciliations.created_at, Reconciliations.id)
        )
        found.extend(session.scalars(stmt).all())
    return found


@translate_db_errors("reconciliations")
def soft_delete_reconciliation(
    session: Session, reconciliation_id: uuid.UUID
) -> Reconciliations:
    """Undoes a match. The unique index is partial, so the pair can be reconciled again."""
    reconciliation = get_reconciliation_by_id(session, reconciliation_id)
    now = datetime.datetime.now(datetime.UTC)
    reconciliation.deleted_at = now
    reconciliation.updated_at = now
    session.flush()
    return reconciliation
