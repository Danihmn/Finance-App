"""Read-only shapes used by the query/analysis endpoints.

They are not tables: they join a stored entity with its owner (the user of the Pluggy item),
or hold the result of an aggregation.
"""

import datetime
import decimal
import uuid
from dataclasses import dataclass, field

from domain.entities import BankAccount, Transaction


@dataclass(slots=True)
class BankAccountWithOwner:
    account: BankAccount
    user_id: uuid.UUID


@dataclass(slots=True)
class TransactionWithOwner:
    transaction: Transaction
    user_id: uuid.UUID


@dataclass(slots=True)
class TransactionFilters:
    """Every field is optional: None means "do not filter by it"."""

    user_id: uuid.UUID | None = None
    bank_account_id: uuid.UUID | None = None
    date_from: datetime.datetime | None = None  # inclusive
    date_to: datetime.datetime | None = None  # exclusive
    type: str | None = None  # DEBIT | CREDIT
    status: str | None = None  # POSTED | PENDING
    category: str | None = None
    search: str | None = None  # case-insensitive, inside the description
    min_amount: decimal.Decimal | None = None  # compared with abs(amount)
    max_amount: decimal.Decimal | None = None


@dataclass(slots=True)
class CurrencyTotals:
    currency_code: str
    total_spent: decimal.Decimal
    total_received: decimal.Decimal
    transaction_count: int


@dataclass(slots=True)
class CategoryTotal:
    currency_code: str
    category: str | None
    total_spent: decimal.Decimal
    transaction_count: int


@dataclass(slots=True)
class UserTotal:
    currency_code: str
    user_id: uuid.UUID
    first_name: str
    total_spent: decimal.Decimal
    transaction_count: int


@dataclass(slots=True)
class SpendingSummary:
    totals: list[CurrencyTotals] = field(default_factory=list)
    by_category: list[CategoryTotal] = field(default_factory=list)
    by_user: list[UserTotal] = field(default_factory=list)
