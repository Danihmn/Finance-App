import logging
from datetime import UTC, date, datetime, time

import httpx
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from domain.entities import Transaction, User
from infra.database.session import get_session
from integrations.pluggy.exceptions.pluggy_exception_error import PluggyExceptionError
from integrations.pluggy.http_clients.account.account_client import get_all_accounts
from integrations.pluggy.http_clients.auth.auth_client import authenticate
from integrations.pluggy.http_clients.transaction.transaction_client import (
    get_all_transactions,
)
from services.bank_accounts_sync_service import sync_bank_account
from services.encryption_service import decrypt
from services.exceptions import ServiceError
from services.pluggy_items_service import list_pluggy_items_by_user
from services.transactions_sync_service import (
    sync_account_transactions,
    to_transaction_entity,
)
from services.users_service import list_users

logger = logging.getLogger(__name__)

_USERS_PAGE_SIZE = 20


def _sync_user_transactions(session: Session, user: User) -> None:
    if user.id is None:
        raise ValueError("User without id")

    api_key = authenticate(
        client_id=user.pluggy_client_id,
        client_secret=decrypt(user.pluggy_client_secret_crypto),
    )
    pluggy_items = list_pluggy_items_by_user(session, user.id)

    for item in pluggy_items:
        try:
            if item.id is None:
                raise ValueError("Pluggy item without id")

            # Both BANK and CREDIT accounts: the transactions logic is the same
            accounts = get_all_accounts(api_key, str(item.pluggy_item_id))
            for account in accounts.results:
                # Our own pluggy_items id, not Pluggy's item id
                stored_account, _ = sync_bank_account(session, item.id, account)
                if stored_account.id is None:
                    raise ValueError("Bank account without id")

                next = None  # Pluggy's pagination approach
                date_from = date.today() - relativedelta(
                    days=1, months=6
                )  # Last 6 months (and D-1, recommended by Pluggy)
                incoming: list[Transaction] = []
                while True:
                    transactions_response = get_all_transactions(
                        api_key,
                        account.id,
                        date_from=date_from.strftime("%Y-%m-%d"),  # 'yyyy-mm-dd' format
                        next=next,
                    )
                    incoming.extend(
                        to_transaction_entity(t, stored_account.id)
                        for t in transactions_response.results
                    )

                    next = transactions_response.next
                    if not next:
                        break

                sync_account_transactions(
                    session,
                    stored_account.id,
                    incoming,
                    datetime.combine(date_from, time.min, tzinfo=UTC),
                )
        except PluggyExceptionError:
            logger.warning(
                "Pluggy error on item %s, skipping it",
                item.pluggy_item_id,
                exc_info=True,
            )


def launch_transactions():
    with get_session() as session:
        offset = 0

        while True:
            users = list_users(session=session, limit=_USERS_PAGE_SIZE, offset=offset)
            if len(users) == 0:
                break

            for user in users:
                try:
                    _sync_user_transactions(session, user)
                    session.commit()
                except ServiceError, PluggyExceptionError, httpx.HTTPError, ValueError:
                    # One user failing must not stop the others
                    session.rollback()
                    logger.exception("Transactions job failed for user %s", user.id)

            offset += _USERS_PAGE_SIZE
