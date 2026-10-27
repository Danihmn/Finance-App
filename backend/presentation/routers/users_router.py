from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from domain.entities import User
from infra.database.session import get_db
from presentation.dependencies import require_admin_key
from presentation.schemas.user_schemas import UserCreate, UserResponse
from services.encryption_service import encrypt
from services.password_hash_service import get_password_hash
from services.users_service import create_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_key)],
)
def create_user_endpoint(
    body: UserCreate, session: Annotated[Session, Depends(get_db)]
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
    return created  # Pydantic can serialize 'User' entity into 'UserResponse' schema
