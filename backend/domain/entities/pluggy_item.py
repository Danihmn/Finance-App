import datetime
import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class PluggyItem:
    user_id: uuid.UUID
    pluggy_item_id: uuid.UUID
    id: uuid.UUID | None = None
    created_at: datetime.datetime | None = None
    consent_expires_at: datetime.datetime | None = None
    last_synced_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None
