import datetime
import decimal
import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class BankAccount:
    pluggy_item_id: uuid.UUID
    pluggy_account_id: uuid.UUID
    type: str
    subtype: str
    name: str
    number: str
    currency_code: str
    id: uuid.UUID | None = None
    created_at: datetime.datetime | None = None
    marketing_name: str | None = None
    tax_number: str | None = None
    owner: str | None = None
    updated_at: datetime.datetime | None = None
    balance: decimal.Decimal | None = None
