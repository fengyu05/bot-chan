from functools import cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fluctlight.settings import SQLALCHEMY_DATABASE_URL, USE_SQL_CHAR_DB


@cache
def create_sessionmaker() -> sessionmaker:
    connect_args = (
        {"check_same_thread": False}
        if SQLALCHEMY_DATABASE_URL.startswith("sqlite")
        else {}
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    if USE_SQL_CHAR_DB:
        SessionLocal = create_sessionmaker()
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None
