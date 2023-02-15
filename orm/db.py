from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession as SAAsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import Config


@lru_cache
def engine_factory():
    return create_async_engine(Config.get("DB_CONNECT"))


def session_factory():
    return sessionmaker(engine_factory(), expire_on_commit=False, class_=SAAsyncSession)()


Base = declarative_base()
