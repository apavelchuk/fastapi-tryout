import uuid
import pytest

from typing import Optional
from sqlalchemy import Column, String

from sqlalchemy_utils.types.uuid import UUIDType
from domain.domain_entity import DomainEntity
from orm.db import Base
from orm.repository import SARepository


class UserSchema(DomainEntity):
    """Test entity for CRUD operations."""

    id: Optional[uuid.UUID]
    username: str
    password: str


class UserModel(Base):
    __tablename__ = "test_user"

    id = Column("id", UUIDType(), primary_key=True, default=uuid.uuid4)
    username = Column("username", String(255), nullable=False)
    password = Column("password", String(255), nullable=False)


class UserRepo(SARepository):
    model = UserModel


@pytest.fixture
async def users(db):
    users = {
        "andrey": UserModel(username="andrey", password="secret0"),
        "paul": UserModel(username="paul", password="secret1"),
        "andrew": UserModel(username="andrew", password="secret2"),
    }
    db.add_all(list(users.values()))
    await db.commit()
    for model in users.values():
        await db.refresh(model)
        db.expunge(model)

    return users
