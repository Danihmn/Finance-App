import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.orm import Session

from domain.entities import User
from infra.database.session import get_db
from infra.jobs.webhook_registration import register_webhooks
from presentation.schemas.user_schemas import UserCreate, UserResponse
from services.encryption_service import encrypt
from services.password_hash_service import get_password_hash
from services.token_service import get_current_user
from services.users_service import create_user, get_user_by_id, list_users

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_user_endpoint(
    background_tasks: BackgroundTasks,
    body: UserCreate,
    session: Annotated[Session, Depends(get_db)],
) -> User:
    user = User(
        first_name=body.first_name,
        email=body.email.lower(),
        hashed_password=get_password_hash(body.password),
        pluggy_client_id=body.pluggy_client_id,
        pluggy_client_secret_crypto=encrypt(body.pluggy_client_secret),
    )
    created = create_user(session, user)
    session.commit()
    background_tasks.add_task(
        register_webhooks
    )  # After created user, it needs to register the user's application webhook
    return created  # Pydantic can serialize 'User' entity into 'UserResponse' schema


@router.get("/me", response_model=UserResponse)
def get_me_endpoint(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


# Both people of the household see each other (the app is private, for two people).
@router.get(
    "",
    response_model=list[UserResponse],
    dependencies=[Depends(get_current_user)],
)
def list_users_endpoint(
    session: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[User]:
    return list_users(session, limit=limit, offset=offset)


# Declared after "/me", otherwise "me" would be read as a user id
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(get_current_user)],
)
def get_user_endpoint(
    user_id: uuid.UUID,
    session: Annotated[Session, Depends(get_db)],
) -> User:
    return get_user_by_id(session, user_id)
