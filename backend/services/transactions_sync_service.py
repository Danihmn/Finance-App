import datetime
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from domain.entities import Transaction
from integrations.pluggy.schemas.transaction.transaction_response_schema import (
    TransactionResponseSchema,
)
from services.transactions_service import (
    list_transactions_since,
    update_transactions,
    upsert_transactions,
)

logger = logging.getLogger(__name__)

# Fields that come from Pluggy and can change between two syncs.
COMPARED_FIELDS = (
    "date",
    "description",
    "description_raw",
    "currency_code",
    "amount",
    "balance",
    "category",
    "category_id",
    "provider_code",
    "provider_id",
    "status",
    "type",
    "operation_type",
    "operation_type_additional_info",
    "amount_in_account_currency",
    "payment_data",
    "credit_card_metadata",
    "merchant",
)

# A change in these invalidates a reconciliation, so it is logged.
_CRITICAL_FIELDS = ("amount", "date", "type")


@dataclass(slots=True)
class SyncResult:
    created: int = 0
    updated: int = 0
    id_changed: int = 0


def to_transaction_entity(
    schema: TransactionResponseSchema, bank_account_id: uuid.UUID
) -> Transaction:
    """Pluggy transaction -> entity. id/created_at stay unset: the database fills them."""
    return Transaction(
        bank_account_id=bank_account_id,
        pluggy_transaction_id=schema.id,
        date=schema.date,
        currency_code=schema.currency_code,
        amount=schema.amount,
        status=schema.status.value,
        type=schema.type.value,
        description=schema.description,
        balance=schema.balance,
        category=schema.category,
        provider_code=schema.provider_code,
        description_raw=schema.description_raw,
        category_id=schema.category_id,
        operation_type=schema.operation_type,
        operation_type_additional_info=schema.operation_type_additional_info,
        provider_id=schema.provider_id,
        amount_in_account_currency=schema.amount_in_account_currency,
        payment_data=schema.payment_data,
        credit_card_metadata=schema.credit_card_metadata,
        merchant=schema.merchant,
    )


def diff_transaction(
    stored: Transaction, incoming: Transaction
) -> dict[str, tuple[Any, Any]]:
    """Fields that differ, as {field: (stored value, incoming value)}."""
    return {
        field: (getattr(stored, field), getattr(incoming, field))
        for field in COMPARED_FIELDS
        if getattr(stored, field) != getattr(incoming, field)
    }


def sync_account_transactions(
    session: Session,
    bank_account_id: uuid.UUID,
    incoming: list[Transaction],
    date_from: datetime.datetime,
) -> SyncResult:
    """Compare Pluggy's transactions with the stored ones in memory and write the
    differences in bulk: one SELECT, one upsert and one update at most."""
    stored = list_transactions_since(session, bank_account_id, date_from)
    by_pluggy_id = {t.pluggy_transaction_id: t for t in stored}
    by_provider_id: dict[str, list[Transaction]] = defaultdict(list)
    for transaction in stored:
        if transaction.provider_id:
            by_provider_id[transaction.provider_id].append(transaction)

    result = SyncResult()
    to_upsert: dict[uuid.UUID, Transaction] = {}  # dedup by pluggy_transaction_id
    to_update: dict[uuid.UUID, Transaction] = {}  # keyed by the stored row's id
    for transaction in incoming:
        current = by_pluggy_id.get(transaction.pluggy_transaction_id)

        if current is None and transaction.provider_id:
            # Not found by Pluggy's id: the institution may have changed it
            # (typical on PENDING -> POSTED), but the provider id stays.
            candidates = by_provider_id.get(transaction.provider_id, [])
            if len(candidates) == 1:
                current = candidates[0]
                if current.id in to_update:
                    continue
                transaction.id = current.id
                to_update[current.id] = transaction  # type: ignore[index]
                result.id_changed += 1
                _log_critical_changes(current, transaction)
                continue
            if len(candidates) > 1:
                logger.warning(
                    "provider_id %s matches %d stored transactions; "
                    "treating pluggy transaction %s as new",
                    transaction.provider_id,
                    len(candidates),
                    transaction.pluggy_transaction_id,
                )

        if current is None:
            if transaction.pluggy_transaction_id not in to_upsert:
                result.created += 1
            to_upsert[transaction.pluggy_transaction_id] = transaction
            continue

        if diff_transaction(current, transaction):
            if transaction.pluggy_transaction_id not in to_upsert:
                result.updated += 1
            _log_critical_changes(current, transaction)
            to_upsert[transaction.pluggy_transaction_id] = transaction

    if to_upsert:
        upsert_transactions(session, list(to_upsert.values()))
    if to_update:
        update_transactions(session, list(to_update.values()))
    return result


def _log_critical_changes(stored: Transaction, incoming: Transaction) -> None:
    changes = diff_transaction(stored, incoming)
    critical = {f: changes[f] for f in _CRITICAL_FIELDS if f in changes}
    if critical:
        logger.warning(
            "transaction %s changed on Pluggy: %s",
            stored.pluggy_transaction_id,
            {f: f"{old} -> {new}" for f, (old, new) in critical.items()},
        )
