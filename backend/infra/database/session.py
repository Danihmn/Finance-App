from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import settings

engine = create_engine(settings.database_url, echo=True)  # type: ignore
Session = sessionmaker(bind=engine, autoflush=False)


@contextmanager
def get_session():
    with Session() as session:
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()
