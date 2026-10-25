import uuid

from sqlalchemy.orm import Session

from domain.entities import Address
from infra.repositories import addresses_repository
from services._mappers import to_entity, to_values
from services.exceptions import translate_repository_errors


@translate_repository_errors
def list_addresses_by_identity_data(
    session: Session, identity_data_id: uuid.UUID
) -> list[Address]:
    addresses = addresses_repository.list_addresses_by_identity_data(
        session, identity_data_id
    )
    return [to_entity(Address, a) for a in addresses]


@translate_repository_errors
def replace_addresses_for_identity_data(
    session: Session, identity_data_id: uuid.UUID, addresses: list[Address]
) -> list[Address]:
    values = [
        {k: v for k, v in to_values(a).items() if k != "identity_data_id"}
        for a in addresses
    ]
    saved = addresses_repository.replace_addresses_for_identity_data(
        session, identity_data_id, values
    )
    return [to_entity(Address, a) for a in saved]
