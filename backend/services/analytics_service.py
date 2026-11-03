from sqlalchemy.orm import Session

from domain.read_models import SpendingSummary, TransactionFilters
from infra.repositories import analytics_repository
from services.exceptions import translate_repository_errors


@translate_repository_errors
def get_spending_summary(
    session: Session, filters: TransactionFilters
) -> SpendingSummary:
    return analytics_repository.get_spending_summary(session, filters)
