from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PluggyModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,  # full_name -> fullName
        validate_by_name=True,  # accepts full_name and fullName
        validate_by_alias=True,
    )


class GeographicCoordinates(PluggyModel):
    latitude: float
    longitude: float


class Addresses(PluggyModel):
    full_address: str | None = None
    primary_address: str | None = None
    city: str | None = None
    postal_code: str | None = None
    state: str | None = None
    country: str | None = None
    country_code: str | None = None
    type: str | None = None
    additional_info: str | None = None
    district: str | None = None
    ibge_town_code: str | None = None
    geographic_coordinates: GeographicCoordinates | None = None


class PhoneNumbers(PluggyModel):
    value: str
    type: str | None = None
    country_calling_code: str | None = None
    area_code: str | None = None
    extension: str | None = None
    additional_info: str | None = None


class Emails(PluggyModel):
    value: str
    type: str | None = None


class Relations(PluggyModel):
    type: str | None = None
    name: str | None = None
    document: str | None = None


class InformedIncome(PluggyModel):
    frequency: str
    amount: Decimal
    date: datetime


class InformedPatrimony(PluggyModel):
    amount: Decimal
    year: int
    date: datetime | None = None


class EconomicActivities(PluggyModel):
    code: str
    is_main: bool


class InformedRevenue(PluggyModel):
    amount: Decimal
    frequency: str | None = None
    frequency_additional_info: str | None = None
    year: int | None = None


class Qualifications(PluggyModel):
    company_cnpj: str
    occupation_code: str | None = None
    occupation_description: str | None = None
    informed_income: InformedIncome | None = None
    informed_patrimony: InformedPatrimony | None = None
    economic_activities: list[EconomicActivities] | None = None
    informed_revenue: InformedRevenue | None = None


class Procurators(PluggyModel):
    type: str
    cpf_number: str
    civil_name: str
    document_number: str | None = None
    document_type: str | None = None
    social_name: str | None = None


class FinancialRelationshipsAccounts(PluggyModel):
    compe_code: str
    branch_code: str
    number: str
    check_digit: str
    type: str
    subtype: str


class PortabilitiesReceived(PluggyModel):
    employer_name: str
    employer_document: str
    paycheck_bank_detainer_cnpj: str
    paycheck_bank_detainer_ispb: str
    portability_approval_date: datetime


class PaychecksBankLink(PluggyModel):
    employer_name: str
    employer_document: str
    paycheck_bank_cnpj: str
    paycheck_bank_ispb: str
    account_opening_date: datetime


class FinancialRelationships(PluggyModel):
    start_date: datetime
    products_services_type: list[str]
    procurators: list[Procurators]
    products_services_type_additional_info: str | None = None
    accounts: list[FinancialRelationshipsAccounts] | None = None
    portabilities_received: list[PortabilitiesReceived] | None = None
    paychecks_bank_link: list[PaychecksBankLink] | None = None


class MaritalStatus(PluggyModel):
    code: str
    additional_info: str | None = None


class NationalityDocument(PluggyModel):
    type: str
    number: str
    country: str | None = None
    issue_date: datetime | None = None
    expiration_date: datetime | None = None
    additional_info: str | None = None


class OtherNationality(PluggyModel):
    country_code: str
    documents: list[NationalityDocument]


class Nationality(PluggyModel):
    has_brazilian_nationality: bool
    other_nationalities: list[OtherNationality] | None = None


class OtherDocuments(PluggyModel):
    type: str
    number: str
    type_additional_info: str | None = None
    check_digit: str | None = None
    additional_info: str | None = None
    expiration_date: datetime | None = None


class Passport(PluggyModel):
    number: str
    country: str
    issue_date: datetime | None = None
    expiration_date: datetime | None = None


class Parties(PluggyModel):
    type: str
    person_type: str
    document_type: str
    document_number: str
    document_country: str | None = None
    document_expiration_date: datetime | None = None
    document_issue_date: datetime | None = None
    document_additional_info: str | None = None
    civil_name: str | None = None
    social_name: str | None = None
    company_name: str | None = None
    trade_name: str | None = None
    start_date: datetime | None = None
    shareholding: Decimal | None = None


class BusinessOtherDocuments(PluggyModel):
    type: str
    number: str
    country: str
    expiration_date: datetime | None = None


class IdentityResponseSchema(PluggyModel):
    id: str
    item_id: UUID
    created_at: datetime
    updated_at: datetime
    birth_date: datetime | None = None
    tax_number: str | None = None
    document: str | None = None
    document_type: str | None = None
    job_title: str | None = None
    full_name: str | None = None
    social_name: str | None = None
    company_name: str | None = None
    establishment_code: str | None = None
    establishment_name: str | None = None
    phone_numbers: list[PhoneNumbers] | None = None
    emails: list[Emails] | None = None
    addresses: list[Addresses] | None = None
    relations: list[Relations] | None = None
    investor_profile: str | None = None
    qualifications: Qualifications | None = None
    financial_relationships: FinancialRelationships | None = None
    sex: str | None = None
    marital_status: MaritalStatus | None = None
    nationality: Nationality | None = None
    other_documents: list[OtherDocuments] | None = None
    passport: Passport | None = None
    incorporation_date: datetime | None = None
    parties: list[Parties] | None = None
    business_other_documents: list[BusinessOtherDocuments] | None = None
    companies_cnpj: list[str] | None = None
