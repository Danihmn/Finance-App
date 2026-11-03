import logging

from sqlalchemy.orm import Session

from domain.entities import User
from integrations.pluggy.config import item_webhook_paths, webhook_token_header
from integrations.pluggy.http_clients.auth.auth_client import authenticate
from integrations.pluggy.http_clients.webhook.webhook_client import (
    create_webhook,
    list_webhooks,
    update_webhook,
)
from integrations.pluggy.schemas.webhook.webhook_response_schema import (
    WebhookResponseSchema,
)
from services.encryption_service import decrypt
from services.users_service import update_user_webhook_secret_hash
from services.webhook_secret_service import (
    generate_webhook_secret,
    hash_webhook_secret,
    verify_webhook_secret,
)

logger = logging.getLogger(__name__)


def _webhook_secret(webhook: WebhookResponseSchema) -> str | None:
    return next(
        (
            value
            for name, value in webhook.headers.items()
            if name.lower() == webhook_token_header.lower()
        ),
        None,
    )


def _secret_matches(webhook: WebhookResponseSchema, secret_hash: str) -> bool:
    secret = _webhook_secret(webhook)
    return secret is not None and verify_webhook_secret(secret, secret_hash)


def ensure_item_webhooks(session: Session, user: User, public_base_url: str) -> None:
    """
    Makes sure the user's Pluggy application has the item webhooks ('item/created', 'item/updated'
    and 'item/deleted') pointing to this backend.

    All of them share the user's one secret. Only its hash is stored, so the plain secret exists just
    when the webhooks are created or the secret is rotated. The rotation happens when any webhook is
    missing or its header does not match the stored hash (hash never saved, database restored, failed
    commit...), and it rewrites the header of every webhook. Pluggy is called first and the database
    after: a failure in between is detected (and fixed) on the next run.
    """
    if user.id is None:
        raise ValueError("User without id")

    base_url = public_base_url.rstrip("/")
    api_key = authenticate(
        client_id=user.pluggy_client_id,
        client_secret=decrypt(user.pluggy_client_secret_crypto),
    )

    registered = list_webhooks(api_key).results
    # event -> its webhook in Pluggy (None when missing)
    webhooks = {
        event: next(
            (
                webhook
                for webhook in registered
                if webhook.event == event and webhook.url == base_url + path
            ),
            None,
        )
        for event, path in item_webhook_paths.items()
    }

    secret_hash = user.pluggy_webhook_secret_hash
    rotate = secret_hash is None or any(
        webhook is None or not _secret_matches(webhook, secret_hash)
        for webhook in webhooks.values()
    )

    if rotate:
        secret = generate_webhook_secret()
        headers = {webhook_token_header: secret}
        for event, webhook in webhooks.items():
            if webhook is None:
                create_webhook(
                    api_key, base_url + item_webhook_paths[event], event, headers
                )
                logger.info("Created the %s webhook for user %s", event, user.id)
            else:
                update_webhook(
                    api_key,
                    str(webhook.id),
                    headers=headers,
                    enabled=True if webhook.disabled_at is not None else None,
                )
                logger.info("Rotated the %s webhook secret for user %s", event, user.id)
        update_user_webhook_secret_hash(session, user.id, hash_webhook_secret(secret))
        return

    for event, webhook in webhooks.items():
        if webhook is not None and webhook.disabled_at is not None:
            update_webhook(api_key, str(webhook.id), enabled=True)
            logger.info("Re-enabled the %s webhook for user %s", event, user.id)
