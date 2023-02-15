import uuid

from pydantic import BaseModel
from typing import List, Optional, Type, Dict, Any

from orm.repository import FindQueryConfig, FilterCondition, Repository


async def create_entity(repo: Repository, entity: BaseModel, response_schema: Type[BaseModel]) -> Type[BaseModel]:
    entity = await repo.create(entity, response_schema)
    return entity


async def get_entities(
    repo: Repository,
    response_schema: BaseModel,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    order_by: Optional[str] = None,
    filters: Optional[FilterCondition] = None,
) -> List[BaseModel]:
    query_config = FindQueryConfig(
        response_schema=response_schema,
        offset=offset,
        limit=limit,
        order_by=order_by,
        conditions=filters,
    )
    entities = []
    async for entity in repo.find(query_config):
        entities.append(entity)
    return entities


async def get_entity(repo: Repository, conditions: List[FilterCondition], response_schema: BaseModel):
    return await repo.find_one(conditions, response_schema)


async def get_entity_count(repo: Repository, filters: Optional[List[FilterCondition]] = None):
    return await repo.count(filters)


async def update_entity(
    repo: Repository, id: uuid.UUID, update_data: Dict[str, Any], response_schema: Type[BaseModel]
) -> BaseModel:
    updated_user = await repo.update_by_id(id, update_data, response_schema)
    return updated_user


async def delete_entity(repo: Repository, conditions: List[FilterCondition]) -> int:
    return await repo.delete(conditions)
