import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.database.models import BankDatas
from infra.repositories._upsert import upsert_one
from infra.repositories.exceptions import translate_db_errors


@translate_db_errors("bank_datas")
def get_bank_data_by_bank_account_id(
    session: Session, bank_account_id: uuid.UUID
) -> BankDatas | None:
    stmt = select(BankDatas).where(BankDatas.bank_account_id == bank_account_id)
    return session.scalars(stmt).one_or_none()


@translate_db_errors("bank_datas")
def upsert_bank_data(session: Session, values: dict[str, Any]) -> BankDatas:
    """Insert or update by bank_account_id (1:1). `values` uses BankDatas column names."""
    return upsert_one(session, BankDatas, values, "bank_account_id")
