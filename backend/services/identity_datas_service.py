import uuid

from sqlalchemy.orm import Session

from domain.entities import IdentityData
from infra.repositories import identity_datas_repository
from services._mappers import to_entity, to_values
from services.exceptions import translate_repository_errors


@translate_repository_errors
def get_identity_data_by_pluggy_item_id(
    session: Session, pluggy_item_id: uuid.UUID
) -> IdentityData | None:
    identity = identity_datas_repository.get_identity_data_by_pluggy_item_id(
        session, pluggy_item_id
    )
    return to_entity(IdentityData, identity) if identity else None


@translate_repository_errors
def upsert_identity_data(session: Session, identity: IdentityData) -> IdentityData:
    saved = identity_datas_repository.upsert_identity_data(session, to_values(identity))
    return to_entity(IdentityData, saved)
