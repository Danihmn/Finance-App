from pydantic import BaseModel, Field


class AccountStatementResponseSchema(BaseModel):
    id: str
    month_year: str = Field(..., alias="monthYear")
    url: str

    class Config:
        populate_by_name = True
