import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from domain.read_models import TransactionWithOwner
from infra.database.session import get_db
from presentation.schemas.common_schemas import Page
from presentation.schemas.transaction_schemas import (
    TransactionQuery,
    TransactionResponse,
)
from services.token_service import get_current_user
from services.transactions_service import (
    get_transaction_with_owner,
    search_transactions,
)

# Both people of the household see every transaction (the app is private, for two people).
router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[Depends(get_current_user)],
)


def _to_response(item: TransactionWithOwner) -> TransactionResponse:
    t = item.transaction
    assert t.id is not None
    return TransactionResponse(
        id=t.id,
        bank_account_id=t.bank_account_id,
        user_id=item.user_id,
        date=t.date,
        description=t.description,
        amount=t.amount,
        currency_code=t.currency_code,
        type=t.type,
        status=t.status,
        category=t.category,
        category_id=t.category_id,
        merchant=t.merchant,
        balance=t.balance,
    )


@router.get("", response_model=Page[TransactionResponse])
def list_transactions_endpoint(
    query: Annotated[TransactionQuery, Query()],
    session: Annotated[Session, Depends(get_db)],
) -> Page[TransactionResponse]:
    items, total = search_transactions(
        session, query.to_filters(), limit=query.limit, offset=query.offset
    )
    return Page[TransactionResponse](
        items=[_to_response(item) for item in items],
        total=total,
        limit=query.limit,
        offset=query.offset,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction_endpoint(
    transaction_id: uuid.UUID,
    session: Annotated[Session, Depends(get_db)],
) -> TransactionResponse:
    return _to_response(get_transaction_with_owner(session, transaction_id))
