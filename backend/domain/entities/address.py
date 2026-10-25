import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class Address:
    identity_data_id: uuid.UUID
    id: uuid.UUID | None = None
    full_address: str | None = None
    primary_address: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    type: str | None = None
    additional_info: str | None = None
