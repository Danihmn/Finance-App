import datetime
import decimal
import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from domain.read_models import TransactionFilters
from presentation.schemas.common_schemas import end_of_day_utc, start_of_day_utc


class TransactionQuery(BaseModel):
    """Query string of GET /transactions. Dates are UTC days: both ends are inclusive."""

    model_config = ConfigDict(extra="forbid")

    user_id: uuid.UUID | None = None
    bank_account_id: uuid.UUID | None = None
    date_from: datetime.date | None = None
    date_to: datetime.date | None = None
    type: Literal["DEBIT", "CREDIT"] | None = None
    status: Literal["POSTED", "PENDING"] | None = None
    category: str | None = Field(default=None, min_length=1, max_length=100)
    search: str | None = Field(default=None, min_length=1, max_length=100)
    min_amount: decimal.Decimal | None = Field(default=None, ge=0)
    max_amount: decimal.Decimal | None = Field(default=None, ge=0)
    exclude_internal: bool = False
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def _check_ranges(self) -> TransactionQuery:
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must not be after date_to")
        if (
            self.min_amount is not None
            and self.max_amount is not None
            and self.min_amount > self.max_amount
        ):
            raise ValueError("min_amount must not be greater than max_amount")
        return self

    def to_filters(self) -> TransactionFilters:
        return TransactionFilters(
            user_id=self.user_id,
            bank_account_id=self.bank_account_id,
            date_from=start_of_day_utc(self.date_from) if self.date_from else None,
            date_to=end_of_day_utc(self.date_to) if self.date_to else None,
            type=self.type,
            status=self.status,
            category=self.category,
            search=self.search,
            min_amount=self.min_amount,
            max_amount=self.max_amount,
            exclude_internal=self.exclude_internal,
        )


class TransactionResponse(BaseModel):
    """`payment_data` is left out on purpose: it carries the other party's document numbers."""

    id: uuid.UUID
    bank_account_id: uuid.UUID
    user_id: uuid.UUID  # The owner of the account
    date: datetime.datetime
    description: str | None
    amount: decimal.Decimal  # Signed as Pluggy sends it. Use `type` for the direction
    currency_code: str
    type: str
    status: str
    category: str | None
    category_id: str | None
    merchant: Any | None
    balance: decimal.Decimal | None
