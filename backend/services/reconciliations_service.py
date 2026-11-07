import uuid

from sqlalchemy.orm import Session

from domain.entities import Reconciliation
from infra.repositories import reconciliations_repository
from services._mappers import to_entity, to_values
from services.exceptions import translate_repository_errors


@translate_repository_errors
def get_reconciliation_by_id(
    session: Session, reconciliation_id: uuid.UUID
) -> Reconciliation:
    reconciliation = reconciliations_repository.get_reconciliation_by_id(
        session, reconciliation_id
    )
    return to_entity(Reconciliation, reconciliation)


@translate_repository_errors
def create_reconciliation(
    session: Session, reconciliation: Reconciliation
) -> Reconciliation:
    created = reconciliations_repository.create_reconciliation(
        session, to_values(reconciliation)
    )
    return to_entity(Reconciliation, created)


@translate_repository_errors
def list_reconciliations_by_entries(
    session: Session, entry_ids: list[uuid.UUID]
) -> list[Reconciliation]:
    reconciliations = reconciliations_repository.list_reconciliations_by_entries(
        session, entry_ids
    )
    return [to_entity(Reconciliation, r) for r in reconciliations]


@translate_repository_errors
def list_reconciliations_by_transactions(
    session: Session, transaction_ids: list[uuid.UUID]
) -> list[Reconciliation]:
    reconciliations = reconciliations_repository.list_reconciliations_by_transactions(
        session, transaction_ids
    )
    return [to_entity(Reconciliation, r) for r in reconciliations]


@translate_repository_errors
def mark_reconciliation_deleted(
    session: Session, reconciliation_id: uuid.UUID
) -> Reconciliation:
    reconciliation = reconciliations_repository.soft_delete_reconciliation(
        session, reconciliation_id
    )
    return to_entity(Reconciliation, reconciliation)
