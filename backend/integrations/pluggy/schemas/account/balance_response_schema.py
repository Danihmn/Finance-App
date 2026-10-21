from pydantic import BaseModel, Field


class BalanceResponseSchema(BaseModel):
    balance: float
    blocked_balance: int = Field(..., alias="blockedBalance")
    automatically_invested_balance: int = Field(
        ..., alias="automaticallyInvestedBalance"
    )
    currency_code: str = Field(..., alias="currencyCode")
    update_date_time: str = Field(..., alias="updateDateTime")

    class Config:
        populate_by_name = True
