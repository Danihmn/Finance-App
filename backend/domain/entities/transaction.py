import datetime
import decimal
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Transaction:
    bank_account_id: uuid.UUID
    pluggy_transaction_id: uuid.UUID
    date: datetime.datetime
    currency_code: str
    amount: decimal.Decimal
    status: str
    type: str
    id: uuid.UUID | None = None
    created_at: datetime.datetime | None = None
    description: str | None = None
    balance: decimal.Decimal | None = None
    category: str | None = None
    provider_code: str | None = None
    updated_at: datetime.datetime | None = None
    description_raw: str | None = None
    category_id: str | None = None
    operation_type: str | None = None
    operation_type_additional_info: str | None = None
    provider_id: str | None = None
    amount_in_account_currency: decimal.Decimal | None = None
    payment_data: Any | None = None
    credit_card_metadata: Any | None = None
    merchant: Any | None = None
