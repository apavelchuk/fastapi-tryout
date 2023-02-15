import uuid

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Optional, Type, Dict, Callable
from pydantic import BaseModel

from . import service
from orm.repository import FilterCondition, Repository
from ..common_schemas import ApiListResponse
from ..utils import get_next_page_url, get_prev_page_url


class URLConf(BaseModel):
    service_handler: Optional[Callable] = None


class GetURLConf(URLConf):
    response_model: Type[BaseModel]


class CreateURLConf(URLConf):
    response_model: Type[BaseModel]
    entity_type: Type[BaseModel]


class ListURLConf(URLConf):
    response_model: Type[ApiListResponse]
    entity_schema: Type[BaseModel]


class UpdateURLConf(URLConf):
    response_model: Type[BaseModel]
    update_schema: Type[BaseModel]


class DeleteURLConf(URLConf):
    pass


def get_available_actions():
    return {
        "get": add_get_action,
        "create": add_create_action,
        "list": add_list_action,
        "update": add_update_action,
        "delete": add_delete_action,
    }


def crud_factory(entity_name: str, router: APIRouter, repo: Repository, actions: Dict[str, URLConf]):
    available_actions = get_available_actions()
    for action_name, handler in available_actions.items():
        if action_name in actions:
            handler(entity_name, router, repo, actions[action_name])
    return router


def add_create_action(entity_name: str, router: APIRouter, repo: Repository, action_conf: CreateURLConf):
    service_handler = service.create_entity
    if action_conf.service_handler:
        service_handler = action_conf.service_handler

    @router.post("/", response_model=action_conf.response_model, summary=f"{entity_name} Create")
    async def create_entity(entity: action_conf.entity_type):  # type: ignore
        created_entity = await service_handler(repo, entity, action_conf.response_model)
        return created_entity

    return create_entity


def add_list_action(entity_name: str, router: APIRouter, repo: Repository, action_conf: ListURLConf):
    service_handler = service.get_entities
    if action_conf.service_handler:
        service_handler = action_conf.service_handler

    @router.get("/", response_model=action_conf.response_model, summary=f"{entity_name} List")
    async def list_entity(offset: int = 0, limit: int = 100, order_by: Optional[str] = None):
        entities = await service_handler(repo, action_conf.entity_schema, offset, limit, order_by)
        count = await service.get_entity_count(repo)

        base_url = router.url_path_for("list_entity")
        return action_conf.response_model(
            results=entities,
            count=count,
            next=get_next_page_url(base_url, offset, limit, count, order_by),
            previous=get_prev_page_url(base_url, offset, limit, order_by),
        )

    return list_entity


def add_update_action(entity_name: str, router: APIRouter, repo: Repository, action_conf: UpdateURLConf):
    service_handler = service.update_entity
    if action_conf.service_handler:
        service_handler = action_conf.service_handler

    @router.patch("/{entity_id}", response_model=action_conf.response_model, summary=f"{entity_name} Update")
    async def update_entity(entity_id: uuid.UUID, update_data: action_conf.update_schema):  # type: ignore
        updated_entity = await service_handler(
            repo,
            entity_id,
            update_data.dict(exclude_unset=True),
            response_schema=action_conf.response_model,
        )
        return updated_entity

    return update_entity


def add_get_action(entity_name: str, router: APIRouter, repo: Repository, action_conf: GetURLConf):
    service_handler = service.get_entity
    if action_conf.service_handler:
        service_handler = action_conf.service_handler

    @router.get("/{entity_id}", response_model=action_conf.response_model, summary=f"{entity_name} Get")
    async def get_entity(entity_id: uuid.UUID):
        entity = await service_handler(
            repo,
            [FilterCondition(field="id", value=entity_id)],
            action_conf.response_model,
        )
        return entity

    return get_entity


def add_delete_action(entity_name: str, router: APIRouter, repo: Repository, action_conf: DeleteURLConf):
    service_handler = service.delete_entity
    if action_conf.service_handler:
        service_handler = action_conf.service_handler

    @router.delete("/{entity_id}", summary=f"{entity_name} Delete")
    async def delete_entity(entity_id: uuid.UUID):
        deleted_amount = await service_handler(repo, [FilterCondition(field="id", value=entity_id)])
        if deleted_amount == 0:
            return JSONResponse(status_code=404, content={"message": "Entity not found."})

    return delete_entity
