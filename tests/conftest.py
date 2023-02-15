import pytest
import os

from unittest import mock
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from config import Config

from orm import db as DB

DEFAULT_TEST_DB_CONNECT = "sqlite+aiosqlite:///test.db"


def _get_declarative_base():
    from tests.orm.conftest import Base

    import orm.user.models

    return Base


@pytest.fixture(autouse=True)
def mock_env_vars():
    mock_map = {
        "DB_CONNECT": Config.get("TEST_DB_CONNECT", DEFAULT_TEST_DB_CONNECT),
    }
    with mock.patch.dict(os.environ, mock_map):
        Config.env.read_env(recurse=True)
        yield


@pytest.fixture(scope="session")
def sync_engine():
    test_db = Config.get("TEST_DB_CONNECT", DEFAULT_TEST_DB_CONNECT).split(":///")[1]
    if os.path.exists(test_db):
        os.remove(test_db)
    engine = create_engine(f"sqlite:///{test_db}")
    _get_declarative_base().metadata.create_all(engine)

    yield engine

    # tear down
    if os.path.exists(test_db):
        os.remove(test_db)


@pytest.fixture
async def db(sync_engine):
    async_engine = DB.engine_factory()
    async with async_engine.connect() as conn:
        await conn.begin()  # root transaction

        child_session = AsyncSession(conn, expire_on_commit=False)
        with mock.patch("orm.repository.session_factory", return_value=child_session):
            yield child_session

        await child_session.close()
        await conn.rollback()  # cancel root transaction
