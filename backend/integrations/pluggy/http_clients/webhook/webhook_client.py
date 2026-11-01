import httpx

from integrations.pluggy.config import base_url
from integrations.pluggy.exceptions.pluggy_exception_error import PluggyExceptionError
from integrations.pluggy.schemas.base_error_schema import BaseErrorSchema
from integrations.pluggy.schemas.base_response_schema import (
    BaseResponseV1Schema,
)
from integrations.pluggy.schemas.webhook.webhook_response_schema import (
    WebhookResponseSchema,
)


def list_webhooks(api_key: str) -> BaseResponseV1Schema[WebhookResponseSchema]:
    """
    Lists all the webhooks associated with the application (headers included)

    Parameters:
            api_key: The authorization API Key
    """
    response = httpx.get(
        f"{base_url}/webhooks",
        headers={"X-API-KEY": api_key},
    )
    if response.is_error:
        try:
            error = BaseErrorSchema.model_validate(response.json())
        except ValueError:
            response.raise_for_status()
            raise

        raise PluggyExceptionError(error)

    return BaseResponseV1Schema[WebhookResponseSchema].model_validate(response.json())


def create_webhook(
    api_key: str, url: str, event: str, headers: dict[str, str] | None = None
) -> WebhookResponseSchema:
    """
    Creates a webhook for the given event

    Parameters:
            api_key: The authorization API Key
            url: Public HTTPS url (default port) that will receive the POST of the event
            event: The event to subscribe to (e.g. 'item/updated'). One event per webhook
            headers: Extra HTTP headers Pluggy sends on every delivery (e.g. our secret token)
    """
    body: dict = {"url": url, "event": event}
    if headers is not None:
        body["headers"] = headers

    response = httpx.post(
        f"{base_url}/webhooks",
        json=body,
        headers={"X-API-KEY": api_key},
    )
    if response.is_error:
        try:
            error = BaseErrorSchema.model_validate(response.json())
        except ValueError:
            response.raise_for_status()
            raise

        raise PluggyExceptionError(error)

    return WebhookResponseSchema.model_validate(response.json())


def update_webhook(
    api_key: str,
    webhook_id: str,
    headers: dict[str, str] | None = None,
    enabled: bool | None = None,
) -> WebhookResponseSchema:
    """
    Updates a webhook. Only the given fields are sent

    Parameters:
            api_key: The authorization API Key
            webhook_id: The webhook's primary identifier
            headers: New extra HTTP headers (replaces the existing ones)
            enabled: True re-enables a webhook that was disabled
    """
    body: dict = {}
    if headers is not None:
        body["headers"] = headers
    if enabled is not None:
        body["enabled"] = enabled

    response = httpx.patch(
        f"{base_url}/webhooks/{webhook_id}",
        json=body,
        headers={"X-API-KEY": api_key},
    )
    if response.is_error:
        try:
            error = BaseErrorSchema.model_validate(response.json())
        except ValueError:
            response.raise_for_status()
            raise

        raise PluggyExceptionError(error)

    return WebhookResponseSchema.model_validate(response.json())
