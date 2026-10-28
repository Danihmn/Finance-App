import datetime
import uuid

from pydantic import AwareDatetime, BaseModel, ConfigDict


class PluggyItemCreate(BaseModel):
    pluggy_item_id: uuid.UUID
    consent_expires_at: AwareDatetime | None = None


class PluggyItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pluggy_item_id: uuid.UUID
    consent_expires_at: datetime.datetime | None
    last_synced_at: datetime.datetime | None
    created_at: datetime.datetime
