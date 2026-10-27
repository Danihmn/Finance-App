import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

from settings import settings


def require_admin_key(x_admin_key: Annotated[str | None, Header()] = None) -> None:
    if x_admin_key is None or not secrets.compare_digest(
        x_admin_key.encode(), settings.admin_api_key.encode()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin key"
        )
