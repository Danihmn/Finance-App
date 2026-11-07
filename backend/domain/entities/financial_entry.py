import datetime
import decimal
import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class FinancialEntry:
    user_id: uuid.UUID
    description: str
    type: str
    amount: decimal.Decimal
    reference_month: datetime.date
    currency_code: str = "BRL"
    status: str = "PLANNED"
    id: uuid.UUID | None = None
    created_at: datetime.datetime | None = None
    bank_account_id: uuid.UUID | None = None
    category: str | None = None
    due_date: datetime.date | None = None
    installment_number: int | None = None
    installment_total: int | None = None
    notes: str | None = None
    updated_at: datetime.datetime | None = None
    deleted_at: datetime.datetime | None = None
