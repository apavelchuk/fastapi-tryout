import uuid

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict

from domain.user import User
from orm.factories import repo_factory
from ..crud import api as crud_api
from ..common_schemas import ApiListResponse
from . import service


class ApiUserEntity(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class ListUserResponse(ApiListResponse):
    results: List[ApiUserEntity]


class PartialUserUpdateSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]


actions: Dict[str, crud_api.URLConf] = {
    "get": crud_api.GetURLConf(response_model=ApiUserEntity),
    "list": crud_api.ListURLConf(response_model=ListUserResponse, entity_schema=ApiUserEntity),
    "create": crud_api.CreateURLConf(
        response_model=ApiUserEntity,
        entity_type=User,
        service_handler=service.create_user,
    ),
    "update": crud_api.UpdateURLConf(response_model=ApiUserEntity, update_schema=PartialUserUpdateSchema),
    "delete": crud_api.DeleteURLConf(),
}
router = crud_api.crud_factory("User", APIRouter(), repo_factory("user"), actions)
