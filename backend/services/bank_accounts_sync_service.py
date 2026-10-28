import logging
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from domain.entities import BankAccount, BankData, CreditData
from integrations.pluggy.schemas.account.account_response_schema import (
    AccountResponseSchema,
    AccountResponseSchemaBankData,
    AccountResponseSchemaCreditData,
)
from services.bank_accounts_service import (
    get_bank_account_by_pluggy_account_id,
    upsert_bank_account,
)
from services.bank_datas_service import (
    get_bank_data_by_bank_account_id,
    upsert_bank_data,
)
from services.credit_datas_service import (
    get_credit_data_by_bank_account_id,
    upsert_credit_data,
)

logger = logging.getLogger(__name__)

# Fields that come from Pluggy and can change between two syncs.
BANK_ACCOUNT_COMPARED_FIELDS = (
    "pluggy_item_id",
    "type",
    "subtype",
    "name",
    "number",
    "currency_code",
    "marketing_name",
    "tax_number",
    "owner",
    "balance",
)
BANK_DATA_COMPARED_FIELDS = (
    "closing_balance",
    "transfer_number",
    "automatically_invested_balance",
    "overdraft_contracted_limit",
    "overdraft_used_limit",
    "unarranged_overdraft_amount",
)
CREDIT_DATA_COMPARED_FIELDS = (
    "level",
    "brand",
    "balance_close_date",
    "balance_due_date",
    "available_credit_limit",
    "balance_foreign_currency",
    "minimum_payment",
    "credit_limit",
    "status",
    "holder_type",
)

# Who the account belongs to / what it is: a change here is unusual, so it is logged.
# Balances and limits change all the time and are not.
_CRITICAL_FIELDS = (
    "pluggy_item_id",
    "type",
    "subtype",
    "currency_code",
    "tax_number",
    "owner",
)


@dataclass(slots=True)
class SyncAccountResult:
    created: bool = False
    updated: bool = False
    data_created: bool = False
    data_updated: bool = False


def to_bank_account_entity(
    schema: AccountResponseSchema, pluggy_item_id: uuid.UUID
) -> BankAccount:
    """Pluggy account -> entity. id/created_at stay unset: the database fills them.

    `pluggy_item_id` is our own pluggy_items id, not Pluggy's item id."""
    return BankAccount(
        pluggy_item_id=pluggy_item_id,
        pluggy_account_id=uuid.UUID(schema.id),
        type=schema.type,
        subtype=schema.subtype,
        name=schema.name,
        number=schema.number,
        currency_code=schema.currency_code,
        marketing_name=schema.marketing_name,
        tax_number=schema.tax_number,
        owner=schema.owner,
        balance=schema.balance,
    )


def to_bank_data_entity(
    schema: AccountResponseSchemaBankData, bank_account_id: uuid.UUID
) -> BankData:
    return BankData(
        bank_account_id=bank_account_id,
        closing_balance=schema.closing_balance,
        transfer_number=schema.transfer_number,
        automatically_invested_balance=schema.automatically_invested_balance,
        overdraft_contracted_limit=schema.overdraft_contracted_limit,
        overdraft_used_limit=schema.overdraft_used_limit,
        unarranged_overdraft_amount=schema.unarranged_overdraft_amount,
    )


def to_credit_data_entity(
    schema: AccountResponseSchemaCreditData, bank_account_id: uuid.UUID
) -> CreditData:
    return CreditData(
        bank_account_id=bank_account_id,
        level=schema.level,
        brand=schema.brand,
        balance_close_date=schema.balance_close_date,
        balance_due_date=schema.balance_due_date,
        available_credit_limit=schema.available_credit_limit,
        balance_foreign_currency=schema.balance_foreign_currency,
        minimum_payment=schema.minimum_payment,
        credit_limit=schema.credit_limit,
        status=schema.status,
        holder_type=schema.holder_type,
    )


def diff_fields(
    stored: Any, incoming: Any, fields: tuple[str, ...]
) -> dict[str, tuple[Any, Any]]:
    """Fields that differ, as {field: (stored value, incoming value)}."""
    return {
        field: (getattr(stored, field), getattr(incoming, field))
        for field in fields
        if getattr(stored, field) != getattr(incoming, field)
    }


def sync_bank_account(
    session: Session, pluggy_item_id: uuid.UUID, schema: AccountResponseSchema
) -> tuple[BankAccount, SyncAccountResult]:
    """Make the stored account (and its bank/credit data) match what Pluggy sent.

    Pluggy is the source of truth: anything that differs in the database is
    overwritten, and nothing is written when nothing differs."""
    result = SyncAccountResult()
    incoming = to_bank_account_entity(schema, pluggy_item_id)
    stored = get_bank_account_by_pluggy_account_id(session, incoming.pluggy_account_id)

    if stored is None:
        account = upsert_bank_account(session, incoming)
        result.created = True
    else:
        changes = diff_fields(stored, incoming, BANK_ACCOUNT_COMPARED_FIELDS)
        if changes:
            _log_critical_changes("account", stored.pluggy_account_id, changes)
            account = upsert_bank_account(session, incoming)
            result.updated = True
        else:
            account = stored

    if account.id is None:
        raise ValueError("Bank account without id")

    if schema.type == "BANK" and schema.bank_data is not None:
        _sync_bank_data(session, account.id, schema.bank_data, result)
    elif schema.type == "CREDIT" and schema.credit_data is not None:
        _sync_credit_data(session, account.id, schema.credit_data, result)

    return account, result


def _sync_bank_data(
    session: Session,
    bank_account_id: uuid.UUID,
    schema: AccountResponseSchemaBankData,
    result: SyncAccountResult,
) -> None:
    incoming = to_bank_data_entity(schema, bank_account_id)
    stored = get_bank_data_by_bank_account_id(session, bank_account_id)
    if stored is None:
        upsert_bank_data(session, incoming)
        result.data_created = True
    elif diff_fields(stored, incoming, BANK_DATA_COMPARED_FIELDS):
        upsert_bank_data(session, incoming)
        result.data_updated = True


def _sync_credit_data(
    session: Session,
    bank_account_id: uuid.UUID,
    schema: AccountResponseSchemaCreditData,
    result: SyncAccountResult,
) -> None:
    incoming = to_credit_data_entity(schema, bank_account_id)
    stored = get_credit_data_by_bank_account_id(session, bank_account_id)
    if stored is None:
        upsert_credit_data(session, incoming)
        result.data_created = True
    elif diff_fields(stored, incoming, CREDIT_DATA_COMPARED_FIELDS):
        upsert_credit_data(session, incoming)
        result.data_updated = True


def _log_critical_changes(
    kind: str, pluggy_id: uuid.UUID, changes: dict[str, tuple[Any, Any]]
) -> None:
    critical = {f: changes[f] for f in _CRITICAL_FIELDS if f in changes}
    if critical:
        logger.warning(
            "%s %s changed on Pluggy: %s",
            kind,
            pluggy_id,
            {f: f"{old} -> {new}" for f, (old, new) in critical.items()},
        )
