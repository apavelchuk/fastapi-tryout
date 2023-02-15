import uuid

from abc import ABC, abstractmethod
from sqlalchemy.sql.expression import Select, Delete
from sqlalchemy import select, asc, desc, update, delete, func
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from enum import Enum
from typing import Type, Final, Optional, Any, List, Union, AsyncIterable

from domain.domain_entity import DomainEntity

from orm.db import Base as SAModel, session_factory
from adapters import convert_model_to_schema, convert_schema_to_model


class RepositoryException(SQLAlchemyError):
    pass


class FilterOps(Enum):
    EQ = "eq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    ILIKE = "ilike"
    LIKE = "like"


class FilterCondition(BaseModel):
    field: str
    operation: Optional[FilterOps] = FilterOps.EQ
    value: Any


class FindQueryConfig(BaseModel):
    response_schema: Type[BaseModel]
    conditions: Optional[List[FilterCondition]] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    order_by: Optional[str] = None
    page: int = 1000

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.order_by is not None:
            self.order_by = self.order_by.split(",")


class Repository(ABC):
    @classmethod
    @abstractmethod
    async def count(cls, query=None, filters: Optional[List[FilterCondition]] = None) -> int:
        pass

    @classmethod
    @abstractmethod
    async def create(cls, entity: DomainEntity, response_schema: BaseModel) -> BaseModel:
        pass

    @classmethod
    @abstractmethod
    def find(cls, query_config: FindQueryConfig, query=None) -> AsyncIterable[BaseModel]:
        pass

    @classmethod
    @abstractmethod
    async def find_one(cls, conditions: List[FilterCondition], response_schema: Type[BaseModel]) -> BaseModel:
        pass

    @classmethod
    @abstractmethod
    async def update_by_id(cls, id: uuid.UUID, values: dict, response_schema: Type[BaseModel]) -> BaseModel:
        pass

    @classmethod
    @abstractmethod
    async def delete(cls, conditions: List[FilterCondition]) -> int:
        pass


def add_filters(model: SAModel, query: Union[Select, Delete], conditions: List[FilterCondition]):
    table = query.get_final_froms()[0] if hasattr(query, "get_final_froms") else query.table
    for filter_cnd in conditions:
        try:
            col = getattr(model, filter_cnd.field)
        except AttributeError:
            raise RepositoryException(f"Field {filter_cnd.field} cannot be found on model {table.name}.")

        if filter_cnd.operation == FilterOps.EQ:
            query = query.where(col == filter_cnd.value)
        elif filter_cnd.operation == FilterOps.LT:
            query = query.where(col < filter_cnd.value)
        elif filter_cnd.operation == FilterOps.LTE:
            query = query.where(col <= filter_cnd.value)
        elif filter_cnd.operation == FilterOps.GT:
            query = query.where(col > filter_cnd.value)
        elif filter_cnd.operation == FilterOps.GTE:
            query = query.where(col >= filter_cnd.value)
        elif filter_cnd.operation == FilterOps.ILIKE:
            query = query.where(col.ilike("%" + filter_cnd.value + "%"))
        elif filter_cnd.operation == FilterOps.LIKE:
            query = query.where(col.like("%" + filter_cnd.value + "%"))

    return query


def config_find_query(model: SAModel, query, query_ctx: FindQueryConfig):
    query = query.execution_options(yield_per=query_ctx.page)

    if query_ctx.conditions is not None:
        query = add_filters(model, query, query_ctx.conditions)
    if query_ctx.offset is not None:
        query = query.offset(query_ctx.offset)
    if query_ctx.limit is not None:
        query = query.limit(query_ctx.limit)
    if query_ctx.order_by:
        order_by = []
        for order_field in query_ctx.order_by:
            field = asc(order_field)
            if order_field.startswith("-"):
                field = desc(order_field[1:])
            order_by.append(field)
        query = query.order_by(*order_by)

    return query


class SARepository(Repository):
    model: Type[SAModel]

    @classmethod
    async def count(cls, query=None, filters: Optional[List[FilterCondition]] = None) -> int:
        if query is not None:
            query = query.with_only_columns(func.count()).order_by(None)
        else:
            query = select(func.count()).select_from(cls.model)
        if filters is not None:
            query = add_filters(cls.model, query, filters)
        async with session_factory() as session:
            count_result = await session.execute(query)
            count = count_result.scalar_one()
        return count

    @classmethod
    async def find(cls, query_config: FindQueryConfig, query=None) -> AsyncIterable[BaseModel]:
        query = query if query is not None else select(cls.model)
        query = config_find_query(cls.model, query, query_config)
        async with session_factory() as session:
            try:
                async_result = await session.stream(query)
                async for row in async_result:
                    yield convert_model_to_schema(row[0], query_config.response_schema)
            except SQLAlchemyError as exc:
                raise RepositoryException(exc)

    @classmethod
    async def find_one(cls, conditions: List[FilterCondition], response_schema: Type[BaseModel]) -> BaseModel:
        query_cnf = FindQueryConfig(conditions=conditions, response_schema=response_schema)
        async for row in cls.find(query_cnf):
            return row
        raise RepositoryException(f"Nothing has been found for model {cls.model.__name__} and conditions: {conditions}")

    @classmethod
    async def create(cls, entity: DomainEntity, response_schema: BaseModel) -> BaseModel:
        model = convert_schema_to_model(entity, cls.model)
        async with session_factory() as session:
            session.add(model)
            try:
                await session.commit()
            except SQLAlchemyError as exc:
                await session.rollback()
                raise RepositoryException(exc)
            await session.refresh(model)
            session.expunge(model)
        return convert_model_to_schema(model, response_schema)

    @classmethod
    async def update_by_id(cls, id: uuid.UUID, values: dict, response_schema: Type[BaseModel]) -> BaseModel:
        query = update(cls.model).where(cls.model.id == id).values(**values)
        async with session_factory() as session:
            try:
                await session.execute(query)
                await session.commit()
            except SQLAlchemyError as exc:
                await session.rollback()
                raise RepositoryException(exc)
        return await cls.find_one(
            [FilterCondition(field="id", value=id)],
            response_schema,
        )

    @classmethod
    async def delete(cls, conditions: List[FilterCondition]) -> int:
        query = add_filters(cls.model, delete(cls.model), conditions)
        async with session_factory() as session:
            try:
                deleted_amount = await session.execute(query)
                await session.commit()
            except SQLAlchemyError as exc:
                await session.rollback()
                raise RepositoryException(exc)
        return deleted_amount.rowcount
