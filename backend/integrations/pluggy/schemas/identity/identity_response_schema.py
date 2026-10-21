from pydantic import BaseModel, Field


class Addresses(BaseModel):
    full_address: str = Field(..., alias="fullAddress")
    country: str
    state: str
    city: str
    postal_code: str = Field(..., alias="postalCode")
    primary_address: str = Field(..., alias="primaryAddress")
    type: str
    additional_info: str = Field(..., alias="additionalInfo")

    class Config:
        populate_by_name = True


class PhoneNumbers(BaseModel):
    type: str
    value: str


class Emails(BaseModel):
    type: str
    value: str


class Relations(BaseModel):
    type: str
    name: str


class IdentityResponseSchema(BaseModel):
    id: str
    item_id: str = Field(..., alias="itemId")
    full_name: str = Field(..., alias="fullName")
    company_name: str = Field(..., alias="companyName")
    document: str
    tax_number: str = Field(..., alias="taxNumber")
    document_type: str = Field(..., alias="documentType")
    job_title: str = Field(..., alias="jobTitle")
    birth_date: str = Field(..., alias="birthDate")
    establishment_code: str = Field(..., alias="establishmentCode")
    establishment_name: str = Field(..., alias="establishmentName")
    addresses: list[Addresses]
    phone_numbers: list[PhoneNumbers] = Field(..., alias="phoneNumbers")
    emails: list[Emails]
    relations: list[Relations]
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")

    class Config:
        populate_by_name = True
