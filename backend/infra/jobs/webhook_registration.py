import logging

import httpx

from infra.database.session import get_session
from integrations.pluggy.exceptions.pluggy_exception_error import PluggyExceptionError
from services.exceptions import ServiceError
from services.pluggy_webhooks_service import ensure_item_updated_webhook
from services.users_service import list_users
from settings import settings

logger = logging.getLogger(__name__)

_USERS_PAGE_SIZE = 20


def register_webhooks() -> None:
    """Registers (or fixes) the Pluggy webhooks of every user. Never raises: it runs at the app's startup"""
    if not settings.public_base_url:
        logger.warning(
            "PUBLIC_BASE_URL is not set, skipping the Pluggy webhook registration"
        )
        return

    with get_session() as session:
        offset = 0

        while True:
            users = list_users(session=session, limit=_USERS_PAGE_SIZE, offset=offset)
            if len(users) == 0:
                break

            for user in users:
                try:
                    ensure_item_updated_webhook(session, user, settings.public_base_url)
                    session.commit()
                except ServiceError, PluggyExceptionError, httpx.HTTPError, ValueError:
                    # One user failing must not stop the others
                    session.rollback()
                    logger.exception("Webhook registration failed for user %s", user.id)

            offset += _USERS_PAGE_SIZE
