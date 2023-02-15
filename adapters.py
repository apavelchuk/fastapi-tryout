from typing import Type
from pydantic import BaseModel

from domain.domain_entity import DomainEntity
from orm.db import Base as SAModel


def convert_model_to_schema(model: SAModel, schema: Type[BaseModel]) -> DomainEntity:
    return schema.from_orm(model)


def convert_schema_to_model(schema: BaseModel, model: Type[SAModel]) -> SAModel:
    return model(**schema.dict())
