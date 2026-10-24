from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

# Columns never overwritten when the row already exists.
_KEEP_ON_CONFLICT = {"id", "created_at"}


def upsert_one[T](
    session: Session,
    model: type[T],
    values: dict[str, Any],
    conflict_column: str,
    set_updated_at: bool = False,
) -> T:
    """INSERT ... ON CONFLICT (conflict_column) DO UPDATE ... RETURNING model."""
    stmt = insert(model).values(**values)
    update_values: dict[str, Any] = {
        key: stmt.excluded[key]
        for key in values
        if key != conflict_column and key not in _KEEP_ON_CONFLICT
    }
    if set_updated_at:
        update_values["updated_at"] = func.now()
    stmt = stmt.on_conflict_do_update(
        index_elements=[conflict_column], set_=update_values
    ).returning(model)
    return session.scalars(stmt, execution_options={"populate_existing": True}).one()
