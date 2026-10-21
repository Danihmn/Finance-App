import httpx
from config import base_url

from integrations.pluggy.exceptions.pluggy_exception_error import PluggyExceptionError
from integrations.pluggy.schemas.base_error_schema import BaseErrorSchema
from integrations.pluggy.schemas.identity.identity_response_schema import (
    IdentityResponseSchema,
)


def get_identity(api_key: str, item_id: str) -> IdentityResponseSchema:
    """
    Recovers identity of an item if available

    Parameters:
            api_key: The authorization API Key
            item_id: Primary item's identifier.
    """
    response = httpx.get(
        f"{base_url}/identity",
        params={"itemId": item_id},
        headers={"X-API-KEY": api_key},
    )
    if response.is_error:
        try:
            error = BaseErrorSchema.model_validate(response.json())
        except ValueError:
            response.raise_for_status()
            raise

        raise PluggyExceptionError(error)

    return IdentityResponseSchema.model_validate(response.json())
