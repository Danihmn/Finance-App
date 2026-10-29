import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.database.models import Users
from infra.repositories.exceptions import RecordNotFoundError, translate_db_errors


@translate_db_errors("users")
def get_user_by_id(session: Session, user_id: uuid.UUID) -> Users:
    user = session.get(Users, user_id)
    if user is None:
        raise RecordNotFoundError("users", "get_user_by_id")
    return user


@translate_db_errors("users")
def get_user_by_email(session: Session, email: str) -> Users | None:
    return session.scalars(select(Users).where(Users.email == email)).one_or_none()


@translate_db_errors("users")
def get_user_by_pluggy_webhook_secret_hash(
    session: Session, secret_hash: str
) -> Users | None:
    stmt = select(Users).where(Users.pluggy_webhook_secret_hash == secret_hash)
    return session.scalars(stmt).one_or_none()


@translate_db_errors("users")
def list_users(session: Session, limit: int = 10, offset: int = 0) -> list[Users]:
    stmt = select(Users).order_by(Users.created_at, Users.id).limit(limit).offset(offset)
    return list(session.scalars(stmt).all())


@translate_db_errors("users")
def create_user(
    session: Session,
    first_name: str,
    email: str,
    hashed_password: str,
    pluggy_client_id: uuid.UUID,
    pluggy_client_secret_crypto: str,
) -> Users:
    user = Users(
        first_name=first_name,
        email=email,
        hashed_password=hashed_password,
        pluggy_client_id=pluggy_client_id,
        pluggy_client_secret_crypto=pluggy_client_secret_crypto,
    )
    session.add(user)
    session.flush()
    return user


@translate_db_errors("users")
def update_user_pluggy_webhook_secret_hash(
    session: Session, user_id: uuid.UUID, secret_hash: str
) -> Users:
    user = get_user_by_id(session, user_id)
    user.pluggy_webhook_secret_hash = secret_hash
    session.flush()
    return user
