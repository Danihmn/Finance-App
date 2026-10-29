from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

_CAMEL_CONFIG = ConfigDict(
    alias_generator=to_camel,  # created_at -> createdAt
    validate_by_name=True,  # accepts created_at and createdAt
    validate_by_alias=True,
)


class WebhookResponseSchema(BaseModel):
    model_config = _CAMEL_CONFIG

    id: UUID
    url: str
    event: str
    headers: dict[str, str]  # Always present; empty when none are configured
    disabled_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
