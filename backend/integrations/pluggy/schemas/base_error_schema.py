from typing import Annotated

from pydantic import BaseModel, Field


class BaseErrorSchema(BaseModel):
    code: int
    message: str
    code_description: Annotated[
        str | None, Field(alias="codeDescription")
    ]  # Distinctive code description, useful to distinguish the error.
    data: str | None = None  # Additional data related to the error, if any
