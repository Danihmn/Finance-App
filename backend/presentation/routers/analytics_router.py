from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from infra.database.session import get_db
from presentation.schemas.analytics_schemas import (
    CategoryTotalResponse,
    CurrencyTotalsResponse,
    SpendingSummaryQuery,
    SpendingSummaryResponse,
    UserTotalResponse,
)
from services.analytics_service import get_spending_summary
from services.token_service import get_current_user

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/spending-summary", response_model=SpendingSummaryResponse)
def spending_summary_endpoint(
    query: Annotated[SpendingSummaryQuery, Query()],
    session: Annotated[Session, Depends(get_db)],
) -> SpendingSummaryResponse:
    """Who spent how much: totals per currency, per category and per person.

    spent = every debit. received = credits on bank accounts (a credit on a card is a bill
    payment or a refund, not income). Without `date_from`/`date_to` it covers all the history.
    """
    summary = get_spending_summary(session, query.to_filters())
    return SpendingSummaryResponse(
        totals=[CurrencyTotalsResponse(**asdict(t)) for t in summary.totals],
        by_category=[CategoryTotalResponse(**asdict(c)) for c in summary.by_category],
        by_user=[UserTotalResponse(**asdict(u)) for u in summary.by_user],
    )
