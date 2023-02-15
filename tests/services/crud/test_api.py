import pytest

from uuid import uuid4
from unittest.mock import patch, AsyncMock
from fastapi import APIRouter
from pydantic import BaseModel

from orm.repository import FilterCondition
from services.common_schemas import ApiListResponse
from services.crud import api
from ...orm.conftest import UserSchema, UserRepo


@pytest.mark.asyncio
async def test_add_create_action():
    user = UserSchema(username="andrew", password="secret")
    urlconf = api.CreateURLConf(response_model=UserSchema, entity_type=UserSchema)
    router = APIRouter()

    service_handler = AsyncMock()
    with patch.object(api.service, "create_entity", service_handler):
        create_handler = api.add_create_action("User", router, UserRepo, urlconf)

    assert len(router.routes) == 1
    route = router.routes[0]
    assert route.methods == {"POST"}
    assert route.summary == "User Create"
    assert route.response_model == UserSchema

    await create_handler(user)
    assert await service_handler.called_once_with(UserRepo, user, UserSchema)


@pytest.mark.asyncio
async def test_add_list_action():
    urlconf = api.ListURLConf(response_model=ApiListResponse, entity_schema=UserSchema)
    router = APIRouter()

    service_handler, count_handler = AsyncMock(return_value=[]), AsyncMock(return_value=0)
    with patch.object(api.service, "get_entities", service_handler):
        list_handler = api.add_list_action("User", router, UserRepo, urlconf)

    assert len(router.routes) == 1
    route = router.routes[0]
    assert route.methods == {"GET"}
    assert route.summary == "User List"
    assert route.response_model == ApiListResponse

    with patch.object(api.service, "get_entity_count", count_handler):
        await list_handler()

    assert await service_handler.called_once_with(UserRepo, UserSchema, 0, 0, None)
    assert await service_handler.called_once_with(UserRepo)


@pytest.mark.asyncio
async def test_add_update_action():
    class UpdateSchema(BaseModel):
        username: str

    urlconf = api.UpdateURLConf(response_model=UserSchema, update_schema=UpdateSchema)
    router = APIRouter()

    service_handler = AsyncMock()
    with patch.object(api.service, "update_entity", service_handler):
        update_handler = api.add_update_action("User", router, UserRepo, urlconf)

    assert len(router.routes) == 1
    route = router.routes[0]
    assert route.methods == {"PATCH"}
    assert route.summary == "User Update"
    assert route.response_model == UserSchema

    entity_id = uuid4()
    update_data = UpdateSchema(username="new user name")
    await update_handler(entity_id, update_data)
    assert await service_handler.called_once_with(UserRepo, entity_id, update_data, UserSchema)


@pytest.mark.asyncio
async def test_add_get_action():
    urlconf = api.GetURLConf(response_model=UserSchema)
    router = APIRouter()

    service_handler = AsyncMock()
    with patch.object(api.service, "get_entity", service_handler):
        get_handler = api.add_get_action("User", router, UserRepo, urlconf)

    assert len(router.routes) == 1
    route = router.routes[0]
    assert route.methods == {"GET"}
    assert route.summary == "User Get"
    assert route.response_model == UserSchema

    entity_id = uuid4()
    await get_handler(entity_id)
    assert await service_handler.called_once_with(UserRepo, [FilterCondition(field="id", value=entity_id)], UserSchema)


@pytest.mark.asyncio
async def test_add_delete_action():
    urlconf = api.DeleteURLConf()
    router = APIRouter()

    service_handler = AsyncMock(return_value=1)
    with patch.object(api.service, "delete_entity", service_handler):
        delete_handler = api.add_delete_action("User", router, UserRepo, urlconf)

    assert len(router.routes) == 1
    route = router.routes[0]
    assert route.methods == {"DELETE"}
    assert route.summary == "User Delete"

    entity_id = uuid4()
    await delete_handler(entity_id)
    assert await service_handler.called_once_with(UserRepo, [FilterCondition(field="id", value=entity_id)])
