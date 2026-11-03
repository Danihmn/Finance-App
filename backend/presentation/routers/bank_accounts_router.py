import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from domain.read_models import BankAccountWithOwner
from infra.database.session import get_db
from presentation.schemas.bank_account_schemas import (
    BankAccountQuery,
    BankAccountResponse,
)
from services.bank_accounts_service import (
    get_bank_account_with_owner,
    search_bank_accounts,
)
from services.token_service import get_current_user

# Both people of the household see every account (the app is private, for two people).
router = APIRouter(
    prefix="/bank-accounts",
    tags=["bank-accounts"],
    dependencies=[Depends(get_current_user)],
)


def _to_response(item: BankAccountWithOwner) -> BankAccountResponse:
    account = item.account
    assert account.id is not None
    return BankAccountResponse(
        id=account.id,
        user_id=item.user_id,
        pluggy_item_id=account.pluggy_item_id,
        type=account.type,
        subtype=account.subtype,
        name=account.name,
        marketing_name=account.marketing_name,
        number=account.number,
        currency_code=account.currency_code,
        owner=account.owner,
        balance=account.balance,
        created_at=account.created_at,
        updated_at=account.updated_at,
    )


@router.get("", response_model=list[BankAccountResponse])
def list_bank_accounts_endpoint(
    query: Annotated[BankAccountQuery, Query()],
    session: Annotated[Session, Depends(get_db)],
) -> list[BankAccountResponse]:
    items = search_bank_accounts(
        session,
        user_id=query.user_id,
        account_type=query.type,
        limit=query.limit,
        offset=query.offset,
    )
    return [_to_response(item) for item in items]


@router.get("/{account_id}", response_model=BankAccountResponse)
def get_bank_account_endpoint(
    account_id: uuid.UUID,
    session: Annotated[Session, Depends(get_db)],
) -> BankAccountResponse:
    return _to_response(get_bank_account_with_owner(session, account_id))
