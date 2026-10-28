import httpx

from integrations.pluggy.config import base_url
from integrations.pluggy.exceptions.pluggy_exception_error import PluggyExceptionError
from integrations.pluggy.schemas.base_error_schema import BaseErrorSchema


def authenticate(client_id, client_secret) -> str:
    """Returns an apiKey string, or raises PluggyError if status_code is not 200"""
    response = httpx.post(
        f"{base_url}/auth",
        json={"clientId": str(client_id), "clientSecret": client_secret},
    )
    if response.is_error:
        try:
            error = BaseErrorSchema.model_validate(response.json())
        except ValueError:
            response.raise_for_status()
            raise

        raise PluggyExceptionError(error)

    return response.json()["apiKey"]
