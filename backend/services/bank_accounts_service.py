import decimal
import uuid

from sqlalchemy.orm import Session

from domain.entities import BankAccount
from infra.repositories import bank_account_repository
from services._mappers import to_entity, to_values
from services.exceptions import translate_repository_errors


@translate_repository_errors
def get_all_stored_bank_accounts(
    session: Session, limit: int = 10, offset: int = 0
) -> list[BankAccount]:
    accounts = bank_account_repository.get_all_stored_bank_accounts(
        session, limit=limit, offset=offset
    )
    return [to_entity(BankAccount, a) for a in accounts]


@translate_repository_errors
def get_bank_account_by_id(session: Session, account_id: uuid.UUID) -> BankAccount:
    account = bank_account_repository.get_bank_account_by_id(session, account_id)
    return to_entity(BankAccount, account)


@translate_repository_errors
def get_bank_account_by_pluggy_account_id(
    session: Session, pluggy_account_id: uuid.UUID
) -> BankAccount | None:
    account = bank_account_repository.get_bank_account_by_pluggy_account_id(
        session, pluggy_account_id
    )
    return to_entity(BankAccount, account) if account else None


@translate_repository_errors
def list_bank_accounts_by_item(
    session: Session, pluggy_item_id: uuid.UUID
) -> list[BankAccount]:
    accounts = bank_account_repository.list_bank_accounts_by_item(
        session, pluggy_item_id
    )
    return [to_entity(BankAccount, a) for a in accounts]


@translate_repository_errors
def upsert_bank_account(session: Session, account: BankAccount) -> BankAccount:
    saved = bank_account_repository.upsert_bank_account(session, to_values(account))
    return to_entity(BankAccount, saved)


@translate_repository_errors
def update_bank_account_balance(
    session: Session, account_id: uuid.UUID, balance: decimal.Decimal | None
) -> BankAccount:
    account = bank_account_repository.update_bank_account_balance(
        session, account_id, balance
    )
    return to_entity(BankAccount, account)
