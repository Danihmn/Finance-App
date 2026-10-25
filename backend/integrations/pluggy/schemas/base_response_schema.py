from pydantic import BaseModel, Field


class BaseResponseV2Schema[T](BaseModel):
    """
    BaseResponseV2Schema (only for list responses)

    results: The V2 response content
    next: The Pluggy's pagination approach next item, to pass as parameter in next requests.
          None means this is the last page

    Just pass to next request the exactly 'next' received
    """

    results: list[T]
    next: str | None = None


class BaseResponseV1Schema[T](BaseModel):
    """
    BaseResponseV1Schema (only for list responses)

    results: The V1 response content
    page: The current page
    total: The total items
    total_pages: The total pages
    """

    page: int
    total: int
    total_pages: int = Field(..., alias="totalPages")
    results: list[T]

    class Config:
        populate_by_name = True
