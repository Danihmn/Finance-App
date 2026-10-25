import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.database.models import PluggyItems
from infra.repositories.exceptions import RecordNotFoundError, translate_db_errors


@translate_db_errors("pluggy_items")
def get_pluggy_item_by_id(session: Session, item_id: uuid.UUID) -> PluggyItems:
    item = session.get(PluggyItems, item_id)
    if item is None:
        raise RecordNotFoundError("pluggy_items", "get_pluggy_item_by_id")
    return item


@translate_db_errors("pluggy_items")
def get_pluggy_item_by_pluggy_item_id(
    session: Session, pluggy_item_id: uuid.UUID
) -> PluggyItems | None:
    stmt = select(PluggyItems).where(PluggyItems.pluggy_item_id == pluggy_item_id)
    return session.scalars(stmt).one_or_none()


@translate_db_errors("pluggy_items")
def list_pluggy_items_by_user(
    session: Session, user_id: uuid.UUID
) -> list[PluggyItems]:
    stmt = (
        select(PluggyItems)
        .where(PluggyItems.user_id == user_id)
        .order_by(PluggyItems.created_at, PluggyItems.id)
    )
    return list(session.scalars(stmt).all())


@translate_db_errors("pluggy_items")
def list_pluggy_items_expiring_before(
    session: Session, limit_date: datetime.datetime
) -> list[PluggyItems]:
    stmt = (
        select(PluggyItems)
        .where(PluggyItems.consent_expires_at.is_not(None))
        .where(PluggyItems.consent_expires_at < limit_date)
        .order_by(PluggyItems.consent_expires_at, PluggyItems.id)
    )
    return list(session.scalars(stmt).all())


@translate_db_errors("pluggy_items")
def create_pluggy_item(
    session: Session,
    user_id: uuid.UUID,
    pluggy_item_id: uuid.UUID,
    consent_expires_at: datetime.datetime | None = None,
) -> PluggyItems:
    item = PluggyItems(
        user_id=user_id,
        pluggy_item_id=pluggy_item_id,
        consent_expires_at=consent_expires_at,
    )
    session.add(item)
    session.flush()
    return item


@translate_db_errors("pluggy_items")
def update_pluggy_item_sync_info(
    session: Session,
    item_id: uuid.UUID,
    last_synced_at: datetime.datetime,
    consent_expires_at: datetime.datetime | None,
) -> PluggyItems:
    item = get_pluggy_item_by_id(session, item_id)
    item.last_synced_at = last_synced_at
    item.consent_expires_at = consent_expires_at
    item.updated_at = datetime.datetime.now(datetime.UTC)
    session.flush()
    return item
