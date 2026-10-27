import datetime
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    first_name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)
    pluggy_client_id: uuid.UUID
    pluggy_client_secret: str = Field(min_length=1)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    first_name: str
    email: str
    created_at: datetime.datetime
