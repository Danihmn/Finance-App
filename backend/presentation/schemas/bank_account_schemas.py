import datetime
import decimal
import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BankAccountQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: uuid.UUID | None = None
    type: Literal["BANK", "CREDIT"] | None = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class BankAccountResponse(BaseModel):
    """`tax_number` (the holder's CPF) is left out on purpose."""

    id: uuid.UUID
    user_id: (
        uuid.UUID
    )  # The owner: the user who connected the item this account belongs to
    pluggy_item_id: uuid.UUID  # Our own pluggy_items.id, not Pluggy's item id
    type: str
    subtype: str
    name: str
    marketing_name: str | None
    number: str
    currency_code: str
    owner: str | None
    balance: decimal.Decimal | None
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None
