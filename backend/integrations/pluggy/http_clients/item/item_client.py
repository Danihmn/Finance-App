import httpx

from integrations.pluggy.config import base_url
from integrations.pluggy.exceptions.pluggy_exception_error import PluggyExceptionError
from integrations.pluggy.schemas.base_error_schema import BaseErrorSchema
from integrations.pluggy.schemas.item.item_response_schema import ItemResponseSchema


def get_item(api_key: str, item_id: str) -> ItemResponseSchema:
    """
    Retrieves an item (its consent expiration date included)

    Parameters:
            api_key: The authorization API Key
            item_id: The item's primary identifier
    """
    response = httpx.get(
        f"{base_url}/items/{item_id}",
        headers={"X-API-KEY": api_key},
    )
    if response.is_error:
        try:
            error = BaseErrorSchema.model_validate(response.json())
        except ValueError:
            response.raise_for_status()
            raise

        raise PluggyExceptionError(error)

    return ItemResponseSchema.model_validate(response.json())
