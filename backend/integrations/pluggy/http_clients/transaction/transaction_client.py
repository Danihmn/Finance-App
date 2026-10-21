from datetime import datetime

import httpx
from config import base_url

from integrations.pluggy.exceptions.pluggy_exception_error import PluggyExceptionError
from integrations.pluggy.schemas.base_error_schema import BaseErrorSchema
from integrations.pluggy.schemas.base_response_schema import (
    BaseResponseV2Schema,
)
from integrations.pluggy.schemas.transaction.transaction_response_schema import (
    TransactionResponseSchema,
)


def get_all_transactions(
    api_key: str,
    account_id: str,
    ids: list[str] | None = None,
    date_from: str | datetime | None = None,
    date_to: str | datetime | None = None,
    created_at_from: str | datetime | None = None,
    after: str | None = None,
) -> BaseResponseV2Schema:
    """
    Get the transactions of an account.

    Parameters:
        api_key: The authorization API Key
        account_id: Primary ID of the account (UUID). Required.
        ids: List of transaction IDs (UUIDs). Maximum of 500 IDs per request.
        date_from: Only return transactions with a date on or after this date.
            Format: yyyy-mm-dd. Cannot be used together with `created_at_from`.
        date_to: Only return transactions with a date on or before this date.
            Format: yyyy-mm-dd.
        created_at_from: Only return transactions created on or after this date.
            Format: yyyy-mm-ddThh:mm:ss.000Z.
        after: Cursor for the next page of results. Use only the decoded
            `after` value from the `next` URL of the previous response,
            never the full `next` string.
    """
    params = {
        "accountId": account_id,
        "ids": ",".join(ids) if ids else None,
        "dateFrom": _to_str(date_from),
        "dateTo": _to_str(date_to),
        "createdAtFrom": _to_str(created_at_from),
        "after": after,
    }
    params = {
        key: value for key, value in params.items() if value is not None
    }  # Ignore None values

    response = httpx.get(
        f"{base_url}/v2/transactions",
        params=params,
        headers={"X-API-KEY": api_key},
    )
    if response.is_error:
        try:
            error = BaseErrorSchema.model_validate(response.json())
        except ValueError:
            response.raise_for_status()
            raise

        raise PluggyExceptionError(error)

    return BaseResponseV2Schema[TransactionResponseSchema].model_validate(
        response.json()
    )


def _to_str(value: str | datetime | None) -> str | None:
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    return value.isoformat()  # date -> yyyy-mm-dd
