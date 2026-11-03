import datetime
import uuid

from sqlalchemy.orm import Session

from domain.entities import Transaction
from domain.read_models import TransactionFilters, TransactionWithOwner
from infra.repositories import transactions_repository
from services._mappers import to_entity, to_values
from services.exceptions import translate_repository_errors


@translate_repository_errors
def get_transaction_by_id(session: Session, transaction_id: uuid.UUID) -> Transaction:
    transaction = transactions_repository.get_transaction_by_id(session, transaction_id)
    return to_entity(Transaction, transaction)


@translate_repository_errors
def get_transaction_by_pluggy_transaction_id(
    session: Session, pluggy_transaction_id: uuid.UUID
) -> Transaction | None:
    transaction = transactions_repository.get_transaction_by_pluggy_transaction_id(
        session, pluggy_transaction_id
    )
    return to_entity(Transaction, transaction) if transaction else None


@translate_repository_errors
def list_transactions_by_provider_id(
    session: Session, bank_account_id: uuid.UUID, provider_id: str
) -> list[Transaction]:
    transactions = transactions_repository.list_transactions_by_provider_id(
        session, bank_account_id, provider_id
    )
    return [to_entity(Transaction, t) for t in transactions]


@translate_repository_errors
def list_transactions_by_account(
    session: Session,
    bank_account_id: uuid.UUID,
    date_from: datetime.datetime | None = None,
    date_to: datetime.datetime | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Transaction]:
    transactions = transactions_repository.list_transactions_by_account(
        session, bank_account_id, date_from, date_to, limit, offset
    )
    return [to_entity(Transaction, t) for t in transactions]


@translate_repository_errors
def upsert_transactions(
    session: Session, transactions: list[Transaction]
) -> list[Transaction]:
    saved = transactions_repository.upsert_transactions(
        session, [to_values(t) for t in transactions]
    )
    return [to_entity(Transaction, t) for t in saved]


@translate_repository_errors
def list_transactions_since(
    session: Session,
    bank_account_id: uuid.UUID,
    date_from: datetime.datetime,
    include_deleted: bool = False,
) -> list[Transaction]:
    transactions = transactions_repository.list_transactions_since(
        session, bank_account_id, date_from, include_deleted
    )
    return [to_entity(Transaction, t) for t in transactions]


@translate_repository_errors
def mark_transactions_deleted(session: Session, ids: list[uuid.UUID]) -> None:
    transactions_repository.soft_delete_transactions(session, ids)


@translate_repository_errors
def update_transactions(session: Session, transactions: list[Transaction]) -> None:
    transactions_repository.update_transactions(
        session, [to_values(t) for t in transactions]
    )


@translate_repository_errors
def search_transactions(
    session: Session,
    filters: TransactionFilters,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[TransactionWithOwner], int]:
    """A page of transactions (newest first) and the total that match the filters."""
    rows = transactions_repository.search_transactions(session, filters, limit, offset)
    total = transactions_repository.count_transactions(session, filters)
    items = [
        TransactionWithOwner(transaction=to_entity(Transaction, t), user_id=user_id)
        for t, user_id in rows
    ]
    return items, total


@translate_repository_errors
def get_transaction_with_owner(
    session: Session, transaction_id: uuid.UUID
) -> TransactionWithOwner:
    transaction, user_id = transactions_repository.get_transaction_with_owner(
        session, transaction_id
    )
    return TransactionWithOwner(
        transaction=to_entity(Transaction, transaction), user_id=user_id
    )
