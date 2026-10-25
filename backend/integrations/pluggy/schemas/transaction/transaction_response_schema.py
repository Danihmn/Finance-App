from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
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
    category_id: str | None = None
    operation_type: str | None = None
    operation_type_additional_info: str | None = None
    amount_in_account_currency: Decimal | None = None
    payment_data: dict[str, Any] | None = None
    credit_card_metadata: dict[str, Any] | None = None
    merchant: dict[str, Any] | None = None

    @field_validator("amount", "balance", "amount_in_account_currency")
    @classmethod
    def _round_to_cents(cls, value: Decimal | None) -> Decimal | None:
        # The database columns are numeric(18, 2); keeping the same scale (and the
        # same tie rounding as Postgres) avoids false differences when comparing.
        if value is None:
            return None
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
