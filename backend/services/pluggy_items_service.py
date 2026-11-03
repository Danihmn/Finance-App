import datetime
import uuid

from sqlalchemy.orm import Session

from domain.entities import PluggyItem
from infra.repositories import pluggy_items_repository
from services._mappers import to_entity
from services.exceptions import AlreadyExistsError, translate_repository_errors


@translate_repository_errors
def get_pluggy_item_by_id(session: Session, item_id: uuid.UUID) -> PluggyItem:
    item = pluggy_items_repository.get_pluggy_item_by_id(session, item_id)
    return to_entity(PluggyItem, item)


@translate_repository_errors
def get_pluggy_item_by_pluggy_item_id(
    session: Session, pluggy_item_id: uuid.UUID
) -> PluggyItem | None:
    item = pluggy_items_repository.get_pluggy_item_by_pluggy_item_id(
        session, pluggy_item_id
    )
    return to_entity(PluggyItem, item) if item else None


@translate_repository_errors
def list_pluggy_items_by_user(session: Session, user_id: uuid.UUID) -> list[PluggyItem]:
    items = pluggy_items_repository.list_pluggy_items_by_user(session, user_id)
    return [to_entity(PluggyItem, i) for i in items]


@translate_repository_errors
def list_pluggy_items_expiring_before(
    session: Session, limit_date: datetime.datetime
) -> list[PluggyItem]:
    items = pluggy_items_repository.list_pluggy_items_expiring_before(
        session, limit_date
    )
    return [to_entity(PluggyItem, i) for i in items]


@translate_repository_errors
def create_pluggy_item(session: Session, item: PluggyItem) -> PluggyItem:
    created = pluggy_items_repository.create_pluggy_item(
        session,
        user_id=item.user_id,
        pluggy_item_id=item.pluggy_item_id,
        consent_expires_at=item.consent_expires_at,
    )
    return to_entity(PluggyItem, created)


def register_pluggy_item_if_missing(
    session: Session,
    user_id: uuid.UUID,
    pluggy_item_id: uuid.UUID,
    consent_expires_at: datetime.datetime | None = None,
) -> tuple[PluggyItem, bool]:
    """
    Idempotent: returns the stored item (deleted ones included) and whether this call created it.
    Pluggy retries webhooks and may send 'item/created' and 'item/updated' together, so the same
    item can arrive twice at the same time: the loser of the insert race gets the winner's row
    """
    existing = get_pluggy_item_by_pluggy_item_id(session, pluggy_item_id)
    if existing is not None:
        return existing, False

    try:
        # Savepoint: a lost race must not poison the caller's transaction
        with session.begin_nested():
            created = create_pluggy_item(
                session,
                PluggyItem(
                    user_id=user_id,
                    pluggy_item_id=pluggy_item_id,
                    consent_expires_at=consent_expires_at,
                ),
            )
    except AlreadyExistsError:
        existing = get_pluggy_item_by_pluggy_item_id(session, pluggy_item_id)
        if existing is None:
            raise
        return existing, False

    return created, True


@translate_repository_errors
def mark_pluggy_item_deleted(session: Session, item_id: uuid.UUID) -> PluggyItem:
    item = pluggy_items_repository.soft_delete_pluggy_item(session, item_id)
    return to_entity(PluggyItem, item)


@translate_repository_errors
def update_pluggy_item_sync_info(
    session: Session,
    item_id: uuid.UUID,
    last_synced_at: datetime.datetime,
    consent_expires_at: datetime.datetime | None,
) -> PluggyItem:
    item = pluggy_items_repository.update_pluggy_item_sync_info(
        session, item_id, last_synced_at, consent_expires_at
    )
    return to_entity(PluggyItem, item)
