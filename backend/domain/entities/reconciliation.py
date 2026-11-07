import datetime
import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class Reconciliation:
    financial_entry_id: uuid.UUID
    transaction_id: uuid.UUID
    source: str = "MANUAL"
    id: uuid.UUID | None = None
    created_at: datetime.datetime | None = None
    notes: str | None = None
    updated_at: datetime.datetime | None = None
    deleted_at: datetime.datetime | None = None
