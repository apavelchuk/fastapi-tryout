import pytest

from uuid import uuid4
from unittest.mock import AsyncMock, patch
from services.crud import service

from ...orm.conftest import UserSchema, UserRepo


@pytest.fixture
def user():
    return UserSchema(id=uuid4(), username="andrew", password="secret")


@pytest.mark.asyncio
async def test_create_entity(user):
    create_mock = AsyncMock(return_value=user)
    with patch.object(UserRepo, "create", create_mock):
        user_created = await service.create_entity(UserRepo, user, UserSchema)
    create_mock.assert_called_once()
    assert user_created == user


@pytest.mark.asyncio
async def test_get_entities(user):
    async def entities():
        yield user

    with patch.object(UserRepo, "find", return_value=entities()):
        entities = await service.get_entities(UserRepo, UserSchema)

    assert entities == [user]


@pytest.mark.asyncio
async def test_get_entity(user):
    find_mock = AsyncMock(return_value=user)
    with patch.object(UserRepo, "find_one", find_mock):
        user_found = await service.get_entity(UserRepo, ["cond1", "cond2"], UserSchema)
    find_mock.assert_called_once_with(["cond1", "cond2"], UserSchema)
    assert user_found == user


@pytest.mark.asyncio
async def test_get_entity_count():
    count_mock = AsyncMock(return_value=5)
    with patch.object(UserRepo, "count", count_mock):
        count = await service.get_entity_count(UserRepo, ["cond1", "cond2"])
    count_mock.assert_called_once_with(["cond1", "cond2"])
    assert count == 5


@pytest.mark.asyncio
async def test_update_entity(user):
    update_mock = AsyncMock(return_value=user)
    updated_data = {"username": "new user name"}
    with patch.object(UserRepo, "update_by_id", update_mock):
        updated = await service.update_entity(UserRepo, user.id, updated_data, UserSchema)
    update_mock.assert_called_once_with(user.id, updated_data, UserSchema)
    assert updated == user


@pytest.mark.asyncio
async def test_delete_entity(user):
    delete_mock = AsyncMock(return_value=5)
    with patch.object(UserRepo, "delete", delete_mock):
        count = await service.delete_entity(UserRepo, ["cond1", "cond2"])
    delete_mock.assert_called_once_with(["cond1", "cond2"])
    assert count == 5
