import datetime
import decimal
import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class CreditData:
    bank_account_id: uuid.UUID
    id: uuid.UUID | None = None
    level: str | None = None
    brand: str | None = None
    balance_close_date: datetime.datetime | None = None
    balance_due_date: datetime.datetime | None = None
    available_credit_limit: decimal.Decimal | None = None
    balance_foreign_currency: decimal.Decimal | None = None
    minimum_payment: decimal.Decimal | None = None
    credit_limit: decimal.Decimal | None = None
    status: str | None = None
    holder_type: str | None = None
