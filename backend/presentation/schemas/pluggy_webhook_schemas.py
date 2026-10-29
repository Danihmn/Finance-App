import uuid

from pydantic import BaseModel, ConfigDict, Field


class PluggyItemEvent(BaseModel):
    """Payload of the item/* webhooks. Fields we don't use are ignored"""

    model_config = ConfigDict(populate_by_name=True)

    event: str
    event_id: uuid.UUID | None = Field(default=None, alias="eventId")
    item_id: uuid.UUID = Field(alias="itemId")
