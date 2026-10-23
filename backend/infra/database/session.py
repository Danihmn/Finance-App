from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import settings

engine = create_engine(url=settings.database_url)  # type: ignore
Session = sessionmaker(bind=engine, autoflush=False)


def get_session():
    with Session() as session:
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()
