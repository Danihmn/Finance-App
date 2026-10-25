import datetime
import uuid
from dataclasses import dataclass


@dataclass(slots=True)
class IdentityData:
    pluggy_item_id: uuid.UUID
    id: uuid.UUID | None = None
    document: str | None = None
    document_type: str | None = None
    full_name: str | None = None
    job_title: str | None = None
    birth_date: datetime.datetime | None = None
