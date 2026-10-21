from pydantic import BaseModel


class BaseResponseSchema[T](BaseModel):
    """
    results: The response content
    next: The Pluggy's pagination approach next item, to pass as parameter in next requests

    Just pass to next request the exactly 'next' received
    """

    results: list[T]
    next: str
