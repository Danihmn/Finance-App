from typing import Annotated

from pydantic import BaseModel, Field


class BaseErrorSchema(BaseModel):
    code: int
    code_description: Annotated[str, Field(alias="codeDescription")]
    message: str
    data: str | None = None
