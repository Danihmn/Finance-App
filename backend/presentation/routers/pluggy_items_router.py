from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from domain.entities import PluggyItem, User
from infra.database.session import get_db
from presentation.schemas.pluggy_item_schemas import (
    PluggyItemCreate,
    PluggyItemResponse,
)
from services.pluggy_items_service import create_pluggy_item
from services.token_service import get_current_user

router = APIRouter(prefix="/pluggy-items", tags=["pluggy-items"])


@router.post(
    "",
    response_model=PluggyItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pluggy_item_endpoint(
    body: PluggyItemCreate,
    session: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PluggyItem:
    if current_user.id is None:
        raise ValueError("User without id")

    # The owner always comes from the JWT, never from the body
    item = PluggyItem(
        user_id=current_user.id,
        pluggy_item_id=body.pluggy_item_id,
        consent_expires_at=body.consent_expires_at,
    )
    created = create_pluggy_item(session, item)
    session.commit()
    return created  # Pydantic can serialize 'PluggyItem' entity into 'PluggyItemResponse' schema
