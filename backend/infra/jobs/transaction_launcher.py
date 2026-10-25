from infra.database.session import get_session
from integrations.pluggy.exceptions.pluggy_exception_error import PluggyExceptionError
from integrations.pluggy.http_clients.account.account_client import get_all_accounts
from integrations.pluggy.http_clients.auth.auth_client import authenticate
from integrations.pluggy.http_clients.transaction.transaction_client import (
    get_all_transactions,
)
from services.exceptions import ServiceError
from services.pluggy_items_service import list_pluggy_items_by_user
from services.users_service import list_users


def launch_transactions():
    with get_session() as session:
        offset = 20

        while True:
            try:
                users = list_users(session=session, offset=offset)
                if len(users) == 0:
                    break

                for user in users:
                    if user.id is None:
                        raise ValueError("User without id")

                    api_key = authenticate(
                        client_id=user.pluggy_client_id,
                        client_secret=user.pluggy_client_secret_crypto,
                    )
                    pluggy_items = list_pluggy_items_by_user(session, user.id)

                    for item in pluggy_items:
                        try:
                            bank_accounts = get_all_accounts(
                                api_key, str(item.pluggy_item_id), "BANK"
                            )
                            for account in bank_accounts.results:
                                transactions = get_all_transactions(api_key, account.id)

                        except PluggyExceptionError:
                            continue
                        except ValueError:
                            raise

                offset += 20
            except ServiceError:
                continue
            except Exception:
                raise
