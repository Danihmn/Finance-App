import uuid

from sqlalchemy.orm import Session

from domain.entities import BankData
from infra.repositories import bank_datas_repository
from services._mappers import to_entity, to_values
from services.exceptions import translate_repository_errors


@translate_repository_errors
def get_bank_data_by_bank_account_id(
    session: Session, bank_account_id: uuid.UUID
) -> BankData | None:
    data = bank_datas_repository.get_bank_data_by_bank_account_id(
        session, bank_account_id
    )
    return to_entity(BankData, data) if data else None


@translate_repository_errors
def upsert_bank_data(session: Session, bank_data: BankData) -> BankData:
    saved = bank_datas_repository.upsert_bank_data(session, to_values(bank_data))
    return to_entity(BankData, saved)
