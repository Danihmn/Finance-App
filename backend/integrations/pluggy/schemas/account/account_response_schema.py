from pydantic import BaseModel, Field


class AccountResponseSchemaBankData(BaseModel):
    transfer_number: str = Field(..., alias="transferNumber")
    closing_balance: int = Field(..., alias="closingBalance")
    automatically_invested_balance: int = Field(
        ..., alias="automaticallyInvestedBalance"
    )
    overdraft_contracted_limit: int = Field(..., alias="overdraftContractedLimit")
    overdraft_used_limit: int = Field(..., alias="overdraftUsedLimit")
    unarranged_overdraft_amount: int = Field(..., alias="unarrangedOverdraftAmount")

    class Config:
        populate_by_name = True


class AccountResponseSchema(BaseModel):
    id: str
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")
    type: str
    subtype: str
    number: str
    name: str
    marketing_name: str = Field(..., alias="marketingName")
    balance: int
    item_id: str = Field(..., alias="itemId")
    tax_number: str = Field(..., alias="taxNumber")
    owner: str
    currency_code: str = Field(..., alias="currencyCode")
    bank_data: AccountResponseSchemaBankData = Field(..., alias="bankData")

    class Config:
        populate_by_name = True
