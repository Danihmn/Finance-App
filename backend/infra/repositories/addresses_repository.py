import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from infra.database.models import Addresses
from infra.repositories.exceptions import translate_db_errors


@translate_db_errors("addresses")
def list_addresses_by_identity_data(
    session: Session, identity_data_id: uuid.UUID
) -> list[Addresses]:
    stmt = (
        select(Addresses)
        .where(Addresses.identity_data_id == identity_data_id)
        .order_by(Addresses.id)
    )
    return list(session.scalars(stmt).all())


@translate_db_errors("addresses")
def replace_addresses_for_identity_data(
    session: Session, identity_data_id: uuid.UUID, addresses: list[dict[str, Any]]
) -> list[Addresses]:
    """Delete the identity's addresses and insert the given ones (1:N, no natural key)."""
    session.execute(
        delete(Addresses).where(Addresses.identity_data_id == identity_data_id)
    )
    rows = [
        Addresses(identity_data_id=identity_data_id, **values) for values in addresses
    ]
    session.add_all(rows)
    session.flush()
    return rows
