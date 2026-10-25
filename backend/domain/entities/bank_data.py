import decimal
import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class BankData:
    bank_account_id: uuid.UUID
    id: uuid.UUID | None = None
    closing_balance: decimal.Decimal | None = None
    transfer_number: str | None = None
    automatically_invested_balance: decimal.Decimal | None = None
    overdraft_contracted_limit: decimal.Decimal | None = None
    overdraft_used_limit: decimal.Decimal | None = None
    unarranged_overdraft_amount: decimal.Decimal | None = None
