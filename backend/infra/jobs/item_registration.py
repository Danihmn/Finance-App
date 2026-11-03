import logging
import uuid

import httpx

from infra.database.session import get_session
from infra.jobs.transaction_launcher import launch_user_transactions
from integrations.pluggy.exceptions.pluggy_exception_error import PluggyExceptionError
from integrations.pluggy.http_clients.auth.auth_client import authenticate
from integrations.pluggy.http_clients.item.item_client import get_item
from services.encryption_service import decrypt
from services.exceptions import ServiceError
from services.pluggy_items_service import register_pluggy_item_if_missing
from services.users_service import get_user_by_id

logger = logging.getLogger(__name__)


def register_user_item(user_id: uuid.UUID, pluggy_item_id: uuid.UUID) -> None:
    """
    Stores a Pluggy item of the user (if missing) and runs its first sync. Never raises: it runs after
    the webhook's response, opening its own session. Pluggy needs a 2XX within 10 seconds
    """
    created = False

    with get_session() as session:
        try:
            user = get_user_by_id(session, user_id)

            consent_expires_at = None
            try:
                api_key = authenticate(
                    client_id=user.pluggy_client_id,
                    client_secret=decrypt(user.pluggy_client_secret_crypto),
                )
                consent_expires_at = get_item(
                    api_key, str(pluggy_item_id)
                ).consent_expires_at
            except PluggyExceptionError, httpx.HTTPError:
                # The item id is what matters: the consent date is not worth losing the item
                logger.warning(
                    "Could not read the consent date of Pluggy item %s",
                    pluggy_item_id,
                    exc_info=True,
                )

            _, created = register_pluggy_item_if_missing(
                session, user_id, pluggy_item_id, consent_expires_at
            )
            session.commit()
        except ServiceError:
            session.rollback()
            logger.exception(
                "Could not register Pluggy item %s of user %s", pluggy_item_id, user_id
            )
            return

    if created:
        logger.info("Registered Pluggy item %s of user %s", pluggy_item_id, user_id)
        launch_user_transactions(user_id)
