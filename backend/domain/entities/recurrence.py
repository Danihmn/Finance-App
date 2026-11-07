import datetime
import decimal
import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class Recurrence:
    type: str
    amount: decimal.Decimal
    currency_code: str = "BRL"
    id: uuid.UUID | None = None
    created_at: datetime.datetime | None = None
    category: str | None = None
    updated_at: datetime.datetime | None = None
    deleted_at: datetime.datetime | None = None
    user_id: uuid.UUID | None = None
