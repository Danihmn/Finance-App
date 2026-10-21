from datetime import datetime

import httpx

from integrations.exceptions.pluggy_exception_error import PluggyExceptionError
from integrations.schemas.base_error_schema import BaseErrorSchema
from integrations.schemas.base_response_schema import BaseResponseSchema
from integrations.schemas.transaction_response_schema import TransactionResponseSchema

base_url = "https://api.pluggy.ai"


def authenticate(client_id, client_secret) -> str:
    """Returns an apiKey string, or raises PluggyError if status_code is not 200"""
    response = httpx.post(
        f"{base_url}/auth", json={"clientId": client_id, "clientSecret": client_secret}
    )
    if response.is_error:
        try:
            error = BaseErrorSchema.model_validate(response.json())
        except ValueError:
            response.raise_for_status()
            raise

        raise PluggyExceptionError(error)

    return response.json()["apiKey"]


def get_all_transactions(
    api_key: str,
    account_id: str,
    ids: list[str] | None = None,
    date_from: str | datetime | None = None,
    date_to: str | datetime | None = None,
    created_at_from: str | datetime | None = None,
    after: str | None = None,
) -> BaseResponseSchema:
    """
    Get the transactions of an account.

    Parameters:
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
    params = {k: v for k, v in params.items() if v is not None}  # Ignore None values

    response = httpx.get(
        f"{base_url}/transactions",
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

    return BaseResponseSchema[TransactionResponseSchema].model_validate(response.json())


def _to_str(value: str | datetime | None) -> str | None:
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    return value.isoformat()  # date -> yyyy-mm-dd
