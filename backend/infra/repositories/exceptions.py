from functools import wraps

from sqlalchemy.exc import (
    IntegrityError,
    InterfaceError,
    OperationalError,
    SQLAlchemyError,
)

# Postgres SQLSTATE codes for integrity errors.
UNIQUE_VIOLATION = "23505"
FOREIGN_KEY_VIOLATION = "23503"
CHECK_VIOLATION = "23514"
NOT_NULL_VIOLATION = "23502"


class RepositoryError(Exception):
    """Base for every database failure raised by a repository.

    The message never includes statement parameters (CPF, e-mail, hashes).
    """

    def __init__(self, entity: str, operation: str, constraint: str | None = None):
        self.entity = entity
        self.operation = operation
        self.constraint = constraint
        message = f"{entity}.{operation} failed"
        if constraint:
            message += f" ({constraint})"
        super().__init__(message)


class DatabaseConnectionError(RepositoryError):
    """The database is down, unreachable or the connection dropped."""


class RecordNotFoundError(RepositoryError):
    """A getter that requires the row did not find it."""


class DuplicateRecordError(RepositoryError):
    """UNIQUE violation."""


class ForeignKeyViolationError(RepositoryError):
    """The parent row does not exist, or a RESTRICT delete was blocked."""


class ConstraintViolationError(RepositoryError):
    """CHECK or NOT NULL violation."""


_INTEGRITY_ERRORS: dict[str, type[RepositoryError]] = {
    UNIQUE_VIOLATION: DuplicateRecordError,
    FOREIGN_KEY_VIOLATION: ForeignKeyViolationError,
    CHECK_VIOLATION: ConstraintViolationError,
    NOT_NULL_VIOLATION: ConstraintViolationError,
}


def _constraint_name(exc: IntegrityError) -> str | None:
    diag = getattr(exc.orig, "diag", None)
    return getattr(diag, "constraint_name", None) or getattr(diag, "column_name", None)


def translate_db_errors(entity: str):
    """Translate SQLAlchemy errors raised by a repository function.

    Exceptions already derived from RepositoryError pass through untouched.
    Nothing is swallowed: the original error stays as __cause__, and the
    rollback is still up to whoever owns the session.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation = func.__name__
            try:
                return func(*args, **kwargs)
            except RepositoryError:
                raise
            except IntegrityError as exc:
                # psycopg2 exposes `pgcode`, psycopg 3 exposes `sqlstate`.
                sqlstate = getattr(exc.orig, "pgcode", None) or getattr(
                    exc.orig, "sqlstate", None
                )
                error_class = _INTEGRITY_ERRORS.get(sqlstate or "", RepositoryError)
                raise error_class(entity, operation, _constraint_name(exc)) from exc
            except (OperationalError, InterfaceError) as exc:
                raise DatabaseConnectionError(entity, operation) from exc
            except SQLAlchemyError as exc:
                raise RepositoryError(entity, operation) from exc

        return wrapper

    return decorator
