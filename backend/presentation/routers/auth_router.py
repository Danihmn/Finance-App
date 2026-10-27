from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from infra.database.session import get_db
from presentation.schemas.auth_schemas import LoginRequest
from services.password_hash_service import get_password_hash, verify_password
from services.token_service import Token, create_access_token
from services.users_service import get_user_by_email
from settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# Verified when the e-mail is unknown, so both failures cost about the same time.
_DUMMY_HASH = get_password_hash("dummy-password")


@router.post("/login", response_model=Token)
def login(body: LoginRequest, session: Annotated[Session, Depends(get_db)]) -> Token:
    user = get_user_by_email(session, body.email.lower())
    hashed = user.hashed_password if user else _DUMMY_HASH
    password_ok = verify_password(body.password, hashed)
    if user is None or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect e-mail or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        {"sub": str(user.id)},
        timedelta(minutes=settings.access_token_expire_minutes),
    )
    return Token(access_token=access_token, token_type="bearer")
