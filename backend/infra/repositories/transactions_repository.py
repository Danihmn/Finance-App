import datetime
import uuid
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from infra.database.models import Transactions
from infra.repositories.exceptions import RecordNotFoundError, translate_db_errors

# Columns never overwritten when the transaction already exists.
_KEEP_ON_CONFLICT = {"id", "created_at", "pluggy_transaction_id", "bank_account_id"}

# Rows per INSERT statement: keeps well under Postgres' 65535 bind parameters limit.
_UPSERT_CHUNK_SIZE = 500


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
        stmt
        .order_by(Transactions.date.desc(), Transactions.id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(stmt).all())


@translate_db_errors("transactions")
def list_transactions_since(
    session: Session, bank_account_id: uuid.UUID, date_from: datetime.datetime
) -> list[Transactions]:
    """Every transaction of the account with date >= date_from (no pagination)."""
    stmt = (
        select(Transactions)
        .where(Transactions.bank_account_id == bank_account_id)
        .where(Transactions.date >= date_from)
        .order_by(Transactions.date, Transactions.id)
    )
    return list(session.scalars(stmt).all())


@translate_db_errors("transactions")
def upsert_transactions(
    session: Session, values_list: list[dict[str, Any]]
) -> list[Transactions]:
    """Insert or update by pluggy_transaction_id. Each dict uses Transactions column names.

    Sent in chunks of _UPSERT_CHUNK_SIZE rows. All dicts must have the same keys.
    """
    saved: list[Transactions] = []
    for start in range(0, len(values_list), _UPSERT_CHUNK_SIZE):
        chunk = values_list[start : start + _UPSERT_CHUNK_SIZE]
        stmt = insert(Transactions).values(chunk)
        update_values = {
            key: stmt.excluded[key] for key in chunk[0] if key not in _KEEP_ON_CONFLICT
        }
        update_values["updated_at"] = func.now()  # type: ignore
        stmt = stmt.on_conflict_do_update(
            index_elements=["pluggy_transaction_id"], set_=update_values
        ).returning(Transactions)
        saved.extend(
            session.scalars(stmt, execution_options={"populate_existing": True}).all()
        )
    return saved


@translate_db_errors("transactions")
def update_transactions(session: Session, values_list: list[dict[str, Any]]) -> None:
    """Bulk UPDATE by primary key. Each dict must have the row's `id`.

    Used when pluggy_transaction_id itself changes, which the upsert cannot do.
    """
    if not values_list:
        return
    now = datetime.datetime.now(datetime.UTC)
    session.execute(
        update(Transactions),
        [{**values, "updated_at": now} for values in values_list],
    )
