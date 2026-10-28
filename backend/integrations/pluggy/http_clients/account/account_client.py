import httpx

from integrations.pluggy.config import base_url
from integrations.pluggy.exceptions.pluggy_exception_error import PluggyExceptionError
from integrations.pluggy.schemas.account.account_response_schema import (
    AccountResponseSchema,
)
from integrations.pluggy.schemas.account.balance_response_schema import (
    BalanceResponseSchema,
)
from integrations.pluggy.schemas.base_error_schema import BaseErrorSchema
from integrations.pluggy.schemas.base_response_schema import (
    BaseResponseV1Schema,
)
from integrations.pluggy.schemas.transaction.transaction_response_schema import (
    TransactionResponseSchema,
)


def get_all_accounts(
    api_key: str, item_id: str, type: str | None = None
) -> BaseResponseV1Schema:
    """
    Gets all the accounts for the given 'item_id'

    Parameters:
            api_key: The authorization API Key
            item_id: Primary item's identifier.
            type: Filter between bank accounts and credit accounts ('BANK' or 'CREDIT'). None returns both
    """
    params = {"itemId": item_id, "type": type}
    params = {
        key: value for key, value in params.items() if value is not None
    }  # Ignore None values

    response = httpx.get(
        f"{base_url}/accounts",
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

    return BaseResponseV1Schema[AccountResponseSchema].model_validate(response.json())


def get_real_time_balance(api_key: str, id: str) -> BalanceResponseSchema:
    """
    Fetches the real-time balance for the account directly from the financial institution connector,
    without requiring a full item sync.

    Parameters:
            api_key: The authorization API Key
            id: The primary account's identifier
    """
    response = httpx.get(
        f"{base_url}/accounts/{id}/balance",
        params={"id": id},
        headers={"X-API-KEY": api_key},
    )
    if response.is_error:
        try:
            error = BaseErrorSchema.model_validate(response.json())
        except ValueError:
            response.raise_for_status()
            raise

        raise PluggyExceptionError(error)

    return BalanceResponseSchema.model_validate(response.json())


def get_account_statement(api_key: str, id: str) -> BaseResponseV1Schema:
    """
    Recovers all statements collected for the account provided

    Parameters:
            api_key: The authorization API Key
            id: The account primary identifier
    """  # Ignore None values

    response = httpx.get(
        f"{base_url}/accounts/{id}/statements",
        params={"id": id},
        headers={"X-API-KEY": api_key},
    )
    if response.is_error:
        try:
            error = BaseErrorSchema.model_validate(response.json())
        except ValueError:
            response.raise_for_status()
            raise

        raise PluggyExceptionError(error)

    return BaseResponseV1Schema[TransactionResponseSchema].model_validate(
        response.json()
    )
