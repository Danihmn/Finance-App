import uuid

from sqlalchemy.orm import Session

from domain.entities import User
from infra.repositories import users_repository
from services._mappers import to_entity
from services.exceptions import translate_repository_errors


@translate_repository_errors
def get_user_by_id(session: Session, user_id: uuid.UUID) -> User:
    return to_entity(User, users_repository.get_user_by_id(session, user_id))


@translate_repository_errors
def get_user_by_email(session: Session, email: str) -> User | None:
    user = users_repository.get_user_by_email(session, email)
    return to_entity(User, user) if user else None


@translate_repository_errors
def list_users(session: Session, limit: int = 10, offset: int = 0) -> list[User]:
    users = users_repository.list_users(session, limit=limit, offset=offset)
    return [to_entity(User, u) for u in users]


@translate_repository_errors
def create_user(session: Session, user: User) -> User:
    created = users_repository.create_user(
        session,
        first_name=user.first_name,
        email=user.email,
        hashed_password=user.hashed_password,
        pluggy_client_id=user.pluggy_client_id,
        pluggy_client_secret_crypto=user.pluggy_client_secret_crypto,
    )
    return to_entity(User, created)
