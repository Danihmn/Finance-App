from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

_CAMEL_CONFIG = ConfigDict(
    alias_generator=to_camel,  # created_at -> createdAt
    validate_by_name=True,  # accepts created_at and createdAt
    validate_by_alias=True,
)


def _round_to_cents(value: Decimal | None) -> Decimal | None:
    # The database columns are numeric(18, 2); keeping the same scale (and the
    # same tie rounding as Postgres) avoids false differences when comparing.
    if value is None:
        return None
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class AccountResponseSchemaBankData(BaseModel):
    model_config = _CAMEL_CONFIG

    transfer_number: str | None = None
    closing_balance: Decimal | None = None
    automatically_invested_balance: Decimal | None = None
    overdraft_contracted_limit: Decimal | None = None
    overdraft_used_limit: Decimal | None = None
    unarranged_overdraft_amount: Decimal | None = None

    @field_validator(
        "closing_balance",
        "automatically_invested_balance",
        "overdraft_contracted_limit",
        "overdraft_used_limit",
        "unarranged_overdraft_amount",
    )
    @classmethod
    def _round(cls, value: Decimal | None) -> Decimal | None:
        return _round_to_cents(value)


class AccountResponseSchemaCreditData(BaseModel):
    model_config = _CAMEL_CONFIG

    level: str | None = None
    brand: str | None = None
    balance_close_date: datetime | None = None
    balance_due_date: datetime | None = None
    available_credit_limit: Decimal | None = None
    balance_foreign_currency: Decimal | None = None
    minimum_payment: Decimal | None = None
    credit_limit: Decimal | None = None
    status: str | None = None
    holder_type: str | None = None

    @field_validator(
        "available_credit_limit",
        "balance_foreign_currency",
        "minimum_payment",
        "credit_limit",
    )
    @classmethod
    def _round(cls, value: Decimal | None) -> Decimal | None:
        return _round_to_cents(value)

    @field_validator("balance_close_date", "balance_due_date")
    @classmethod
    def _as_utc(cls, value: datetime | None) -> datetime | None:
        # Pluggy may send a plain date ("2022-01-03"); the column is timestamptz,
        # so an aware value avoids false differences when comparing.
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class AccountResponseSchema(BaseModel):
    model_config = _CAMEL_CONFIG

    id: str
    created_at: datetime
    updated_at: datetime
    type: str
    subtype: str
    number: str
    name: str
    marketing_name: str | None = None
    balance: Decimal
    item_id: str
    tax_number: str | None = None
    owner: str | None = None
    currency_code: str
    bank_data: AccountResponseSchemaBankData | None = None
    credit_data: AccountResponseSchemaCreditData | None = None

    @field_validator("balance")
    @classmethod
    def _round_balance(cls, value: Decimal) -> Decimal:
        return _round_to_cents(value)  # type: ignore[return-value]
