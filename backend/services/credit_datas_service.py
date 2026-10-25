import uuid

from sqlalchemy.orm import Session

from domain.entities import CreditData
from infra.repositories import credit_datas_repository
from services._mappers import to_entity, to_values
from services.exceptions import translate_repository_errors


@translate_repository_errors
def get_credit_data_by_bank_account_id(
    session: Session, bank_account_id: uuid.UUID
) -> CreditData | None:
    data = credit_datas_repository.get_credit_data_by_bank_account_id(
        session, bank_account_id
    )
    return to_entity(CreditData, data) if data else None


@translate_repository_errors
def upsert_credit_data(session: Session, credit_data: CreditData) -> CreditData:
    saved = credit_datas_repository.upsert_credit_data(session, to_values(credit_data))
    return to_entity(CreditData, saved)
