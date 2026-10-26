from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import settings

engine = create_engine(settings.database_url, echo=True)  # type: ignore
Session = sessionmaker(bind=engine, autoflush=False)


@contextmanager
def get_session():
    """For scripts and other features that don't use FastAPI's Depends(...)"""
    with Session() as session:
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()


def get_db():
    """Use it for FastAPI's Depends(...)"""
    with Session() as session:
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()
