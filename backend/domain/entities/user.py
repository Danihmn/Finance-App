import datetime
import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class User:
    first_name: str
    email: str
    hashed_password: str
    pluggy_client_id: uuid.UUID
    pluggy_client_secret_crypto: str
    id: uuid.UUID | None = None
    created_at: datetime.datetime | None = None
