import datetime
import decimal
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator

from domain.read_models import TransactionFilters
from presentation.schemas.common_schemas import end_of_day_utc, start_of_day_utc


class SpendingSummaryQuery(BaseModel):
    """Query string of GET /analytics/spending-summary. Dates are UTC days, both inclusive."""

    model_config = ConfigDict(extra="forbid")

    user_id: uuid.UUID | None = None
    bank_account_id: uuid.UUID | None = None
    date_from: datetime.date | None = None
    date_to: datetime.date | None = None
    include_pending: bool = False
    exclude_internal: bool = Field(
        default=True,
        description="Ignore credit card bill payments and transfers between your own accounts",
    )

    @model_validator(mode="after")
    def _check_dates(self) -> SpendingSummaryQuery:
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must not be after date_to")
        return self

    def to_filters(self) -> TransactionFilters:
        return TransactionFilters(
            user_id=self.user_id,
            bank_account_id=self.bank_account_id,
            date_from=start_of_day_utc(self.date_from) if self.date_from else None,
            date_to=end_of_day_utc(self.date_to) if self.date_to else None,
            status=None if self.include_pending else "POSTED",
            exclude_internal=self.exclude_internal,
        )


class CurrencyTotalsResponse(BaseModel):
    currency_code: str
    total_spent: decimal.Decimal
    total_received: decimal.Decimal
    transaction_count: int


class CategoryTotalResponse(BaseModel):
    currency_code: str
    category: str | None
    total_spent: decimal.Decimal
    transaction_count: int


class UserTotalResponse(BaseModel):
    currency_code: str
    user_id: uuid.UUID
    first_name: str
    total_spent: decimal.Decimal
    transaction_count: int


class SpendingSummaryResponse(BaseModel):
    totals: list[CurrencyTotalsResponse]
    by_category: list[CategoryTotalResponse]
    by_user: list[UserTotalResponse]
