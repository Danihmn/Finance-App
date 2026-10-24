import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.database.models import IdentityDatas
from infra.repositories._upsert import upsert_one
from infra.repositories.exceptions import translate_db_errors


@translate_db_errors("identity_datas")
def get_identity_data_by_pluggy_item_id(
    session: Session, pluggy_item_id: uuid.UUID
) -> IdentityDatas | None:
    stmt = select(IdentityDatas).where(IdentityDatas.pluggy_item_id == pluggy_item_id)
    return session.scalars(stmt).one_or_none()


@translate_db_errors("identity_datas")
def upsert_identity_data(session: Session, values: dict[str, Any]) -> IdentityDatas:
    """Insert or update by pluggy_item_id (1:1). `values` uses IdentityDatas column names."""
    return upsert_one(session, IdentityDatas, values, "pluggy_item_id")
