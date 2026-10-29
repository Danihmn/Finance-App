from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from domain.entities import User
from infra.database.session import get_db
from infra.jobs.transaction_launcher import launch_user_transactions
from integrations.pluggy.config import item_updated_webhook_path, webhook_token_header
from presentation.schemas.pluggy_webhook_schemas import PluggyItemEvent
from services.exceptions import NotFoundError
from services.pluggy_items_service import get_pluggy_item_by_pluggy_item_id
from services.users_service import get_user_by_webhook_secret_hash
from services.webhook_secret_service import hash_webhook_secret

router = APIRouter(tags=["pluggy-webhooks"])


def get_webhook_user(
    session: Annotated[Session, Depends(get_db)],
    token: Annotated[str | None, Header(alias=webhook_token_header)] = None,
) -> User:
    """The user (Pluggy application) that owns the secret sent in the webhook's header"""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid webhook token",
    )
    if not token:
        raise unauthorized
    user = get_user_by_webhook_secret_hash(session, hash_webhook_secret(token))
    if user is None:
        raise unauthorized
    return user


@router.post(item_updated_webhook_path, status_code=status.HTTP_202_ACCEPTED)
def item_updated_webhook(
    body: PluggyItemEvent,
    background_tasks: BackgroundTasks,
    session: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_webhook_user)],
) -> None:
    if user.id is None:
        raise ValueError("User without id")

    # The item must belong to the application that sent the webhook
    item = get_pluggy_item_by_pluggy_item_id(session, body.item_id)
    if item is None or item.user_id != user.id:
        raise NotFoundError("Pluggy item not found for this user")

    # Pluggy needs a 2XX within 10 seconds: the sync runs after the response
    background_tasks.add_task(launch_user_transactions, user.id)
