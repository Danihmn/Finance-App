from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

_CAMEL_CONFIG = ConfigDict(
    alias_generator=to_camel,  # consent_expires_at -> consentExpiresAt
    validate_by_name=True,  # accepts consent_expires_at and consentExpiresAt
    validate_by_alias=True,
)


class ItemResponseSchema(BaseModel):
    """Only the fields we use of 'GET /items/{id}'. The others are ignored"""

    model_config = _CAMEL_CONFIG

    id: UUID
    status: str
    execution_status: str
    consent_expires_at: datetime | None = None
    last_updated_at: datetime | None = None
