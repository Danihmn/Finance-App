import datetime
import decimal
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.database.models import BankAccounts, PluggyItems
from infra.repositories._upsert import upsert_one
from infra.repositories.exceptions import RecordNotFoundError, translate_db_errors


@translate_db_errors("bank_accounts")
def get_all_stored_bank_accounts(
    session: Session, limit: int = 10, offset: int = 0
) -> list[BankAccounts]:
    stmt = (
        select(BankAccounts)
        .order_by(BankAccounts.created_at, BankAccounts.id)
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(stmt).all())


@translate_db_errors("bank_accounts")
def get_bank_account_by_id(session: Session, account_id: uuid.UUID) -> BankAccounts:
    account = session.get(BankAccounts, account_id)
    if account is None:
        raise RecordNotFoundError("bank_accounts", "get_bank_account_by_id")
    return account


@translate_db_errors("bank_accounts")
def get_bank_account_by_pluggy_account_id(
    session: Session, pluggy_account_id: uuid.UUID
) -> BankAccounts | None:
    stmt = select(BankAccounts).where(
        BankAccounts.pluggy_account_id == pluggy_account_id
    )
    return session.scalars(stmt).one_or_none()


@translate_db_errors("bank_accounts")
def list_bank_accounts_by_item(
    session: Session, pluggy_item_id: uuid.UUID
) -> list[BankAccounts]:
    stmt = (
        select(BankAccounts)
        .where(BankAccounts.pluggy_item_id == pluggy_item_id)
        .order_by(BankAccounts.created_at, BankAccounts.id)
    )
    return list(session.scalars(stmt).all())


@translate_db_errors("bank_accounts")
def upsert_bank_account(session: Session, values: dict[str, Any]) -> BankAccounts:
    """Insert or update by pluggy_account_id. `values` uses BankAccounts column names."""
    return upsert_one(
        session, BankAccounts, values, "pluggy_account_id", set_updated_at=True
    )


@translate_db_errors("bank_accounts")
def update_bank_account_balance(
    session: Session, account_id: uuid.UUID, balance: decimal.Decimal | None
) -> BankAccounts:
    account = get_bank_account_by_id(session, account_id)
    account.balance = balance
    account.updated_at = datetime.datetime.now(datetime.UTC)
    session.flush()
    return account


def _with_owner(stmt):
    return stmt.join(PluggyItems, BankAccounts.pluggy_item_id == PluggyItems.id)


@translate_db_errors("bank_accounts")
def search_bank_accounts(
    session: Session,
    user_id: uuid.UUID | None = None,
    account_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[tuple[BankAccounts, uuid.UUID]]:
    """Accounts with the owner's user id. Accounts of deleted items stay: their history is kept."""
    stmt = _with_owner(select(BankAccounts, PluggyItems.user_id))
    if user_id is not None:
        stmt = stmt.where(PluggyItems.user_id == user_id)
    if account_type is not None:
        stmt = stmt.where(BankAccounts.type == account_type)
    stmt = (
        stmt.order_by(BankAccounts.created_at, BankAccounts.id)
        .limit(limit)
        .offset(offset)
    )
    return [(account, owner_id) for account, owner_id in session.execute(stmt)]


@translate_db_errors("bank_accounts")
def get_bank_account_with_owner(
    session: Session, account_id: uuid.UUID
) -> tuple[BankAccounts, uuid.UUID]:
    stmt = _with_owner(select(BankAccounts, PluggyItems.user_id)).where(
        BankAccounts.id == account_id
    )
    row = session.execute(stmt).one_or_none()
    if row is None:
        raise RecordNotFoundError("bank_accounts", "get_bank_account_with_owner")
    return row[0], row[1]
