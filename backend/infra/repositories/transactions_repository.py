import datetime
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from infra.database.models import Transactions
from infra.repositories.exceptions import RecordNotFoundError, translate_db_errors

# Columns never overwritten when the transaction already exists.
_KEEP_ON_CONFLICT = {"id", "created_at", "pluggy_transaction_id", "bank_account_id"}


@translate_db_errors("transactions")
def get_transaction_by_id(session: Session, transaction_id: uuid.UUID) -> Transactions:
    transaction = session.get(Transactions, transaction_id)
    if transaction is None:
        raise RecordNotFoundError("transactions", "get_transaction_by_id")
    return transaction


@translate_db_errors("transactions")
def get_transaction_by_pluggy_transaction_id(
    session: Session, pluggy_transaction_id: uuid.UUID
) -> Transactions | None:
    stmt = select(Transactions).where(
        Transactions.pluggy_transaction_id == pluggy_transaction_id
    )
    return session.scalars(stmt).one_or_none()


@translate_db_errors("transactions")
def list_transactions_by_provider_id(
    session: Session, bank_account_id: uuid.UUID, provider_id: str
) -> list[Transactions]:
    """Used to match a PENDING transaction with its POSTED version."""
    stmt = (
        select(Transactions)
        .where(Transactions.bank_account_id == bank_account_id)
        .where(Transactions.provider_id == provider_id)
        .order_by(Transactions.date, Transactions.id)
    )
    return list(session.scalars(stmt).all())


@translate_db_errors("transactions")
def list_transactions_by_account(
    session: Session,
    bank_account_id: uuid.UUID,
    date_from: datetime.datetime | None = None,
    date_to: datetime.datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Transactions]:
    stmt = select(Transactions).where(Transactions.bank_account_id == bank_account_id)
    if date_from is not None:
        stmt = stmt.where(Transactions.date >= date_from)
    if date_to is not None:
        stmt = stmt.where(Transactions.date < date_to)
    stmt = (
        stmt.order_by(Transactions.date.desc(), Transactions.id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(stmt).all())


@translate_db_errors("transactions")
def upsert_transactions(
    session: Session, values_list: list[dict[str, Any]]
) -> list[Transactions]:
    """Insert or update by pluggy_transaction_id. Each dict uses Transactions column names."""
    if not values_list:
        return []
    stmt = insert(Transactions).values(values_list)
    update_values = {
        key: stmt.excluded[key]
        for key in values_list[0]
        if key not in _KEEP_ON_CONFLICT
    }
    stmt = stmt.on_conflict_do_update(
        index_elements=["pluggy_transaction_id"], set_=update_values
    ).returning(Transactions)
    return list(
        session.scalars(stmt, execution_options={"populate_existing": True}).all()
    )
