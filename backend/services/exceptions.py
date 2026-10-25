from functools import wraps

from infra.repositories.exceptions import (
    ConstraintViolationError,
    DatabaseConnectionError,
    DuplicateRecordError,
    ForeignKeyViolationError,
    RecordNotFoundError,
    RepositoryError,
)


class ServiceError(Exception):
    """Base for every failure raised by a service."""


class NotFoundError(ServiceError):
    """The requested record does not exist."""


class AlreadyExistsError(ServiceError):
    """The record violates a uniqueness rule."""


class InvalidDataError(ServiceError):
    """The data breaks a relation or a column rule (FK, CHECK, NOT NULL)."""


class ServiceUnavailableError(ServiceError):
    """The database is unreachable."""


_ERRORS: dict[type[RepositoryError], type[ServiceError]] = {
    RecordNotFoundError: NotFoundError,
    DuplicateRecordError: AlreadyExistsError,
    ForeignKeyViolationError: InvalidDataError,
    ConstraintViolationError: InvalidDataError,
    DatabaseConnectionError: ServiceUnavailableError,
}


def translate_repository_errors(func):
    """Translate RepositoryError into ServiceError, keeping the original as __cause__."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RepositoryError as exc:
            error_class = next(
                (v for k, v in _ERRORS.items() if isinstance(exc, k)), ServiceError
            )
            raise error_class(str(exc)) from exc

    return wrapper
