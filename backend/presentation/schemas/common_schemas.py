import datetime

from pydantic import BaseModel


class Page[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int


def start_of_day_utc(day: datetime.date) -> datetime.datetime:
    return datetime.datetime.combine(day, datetime.time.min, tzinfo=datetime.UTC)


def end_of_day_utc(day: datetime.date) -> datetime.datetime:
    """Exclusive upper bound that includes the whole `day` (the next UTC midnight)."""
    return start_of_day_utc(day + datetime.timedelta(days=1))
