import logging

from sqlalchemy.orm import Session

from domain.entities import User
from integrations.pluggy.config import item_updated_webhook_path, webhook_token_header
from integrations.pluggy.http_clients.auth.auth_client import authenticate
from integrations.pluggy.http_clients.web_hook.webhook_client import (
    create_webhook,
    list_webhooks,
    update_webhook,
)
from services.encryption_service import decrypt
from services.users_service import update_user_webhook_secret_hash
from services.webhook_secret_service import (
    generate_webhook_secret,
    hash_webhook_secret,
    verify_webhook_secret,
)

logger = logging.getLogger(__name__)

ITEM_UPDATED_EVENT = "item/updated"


def ensure_item_updated_webhook(
    session: Session, user: User, public_base_url: str
) -> None:
    """
    Makes sure the user's Pluggy application has the 'item/updated' webhook pointing to this backend.

    Only the secret's hash is stored, so the plain secret exists just when a webhook is created or its
    secret is rotated. The rotation happens when the webhook's header does not match the stored hash
    (webhook missing, hash never saved, database restored, failed commit...). Pluggy is called first and
    the database after: a failure in between is detected (and fixed) on the next run.
    """
    if user.id is None:
        raise ValueError("User without id")

    url = public_base_url.rstrip("/") + item_updated_webhook_path
    api_key = authenticate(
        client_id=user.pluggy_client_id,
        client_secret=decrypt(user.pluggy_client_secret_crypto),
    )

    webhook = next(
        (
            w
            for w in list_webhooks(api_key).results
            if w.event == ITEM_UPDATED_EVENT and w.url == url
        ),
        None,
    )

    if webhook is None:
        secret = generate_webhook_secret()
        create_webhook(api_key, url, ITEM_UPDATED_EVENT, {webhook_token_header: secret})
        update_user_webhook_secret_hash(session, user.id, hash_webhook_secret(secret))
        logger.info("Created the %s webhook for user %s", ITEM_UPDATED_EVENT, user.id)
        return

    current_secret = next(
        (
            value
            for name, value in webhook.headers.items()
            if name.lower() == webhook_token_header.lower()
        ),
        None,
    )
    secret_matches = (
        current_secret is not None
        and user.pluggy_webhook_secret_hash is not None
        and verify_webhook_secret(current_secret, user.pluggy_webhook_secret_hash)
    )

    if not secret_matches:
        secret = generate_webhook_secret()
        update_webhook(
            api_key,
            str(webhook.id),
            headers={webhook_token_header: secret},
            enabled=True if webhook.disabled_at is not None else None,
        )
        update_user_webhook_secret_hash(session, user.id, hash_webhook_secret(secret))
        logger.info(
            "Rotated the %s webhook secret for user %s", ITEM_UPDATED_EVENT, user.id
        )
    elif webhook.disabled_at is not None:
        update_webhook(api_key, str(webhook.id), enabled=True)
        logger.info(
            "Re-enabled the %s webhook for user %s", ITEM_UPDATED_EVENT, user.id
        )
