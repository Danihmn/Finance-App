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


class AccountResponseSchemaCreditData(BaseModel):
    level: str
    brand: str
    balance_close_date: str = Field(..., alias="balanceCloseDate")
    balance_due_date: str = Field(..., alias="balanceDueDate")
    available_credit_limit: int = Field(..., alias="availableCreditLimit")
    balance_foreign_currency: int = Field(..., alias="balanceForeignCurrency")
    minimum_payment: int = Field(..., alias="minimumPayment")
    credit_limit: int = Field(..., alias="creditLimit")
    status: str
    holder_type: str = Field(..., alias="holderType")

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
    creditData: AccountResponseSchemaCreditData = Field(..., alias="creditData")

    class Config:
        populate_by_name = True
