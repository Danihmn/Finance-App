from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class TransactionStatus(StrEnum):
    POSTED = "POSTED"
    PENDING = "PENDING"


class TransactionType(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class TransactionResponseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,  # created_at -> createdAt
        validate_by_name=True,  # accepts created_at and createdAt
        validate_by_alias=True,
    )

    id: UUID
    account_id: UUID
    created_at: datetime
    updated_at: datetime
    date: datetime
    description: str
    description_raw: str | None = None
    currency_code: Annotated[str, Field(min_length=3, max_length=3)]
    amount: Decimal
    balance: Decimal | None = None
    category: str | None = None
    provider_code: str | None = None
    provider_id: str | None = None
    status: TransactionStatus
    type: TransactionType
    payment_data: dict[str, Any] | None = None
