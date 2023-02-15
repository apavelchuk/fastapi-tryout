import uuid

from sqlalchemy import Column, String
from sqlalchemy_utils.types.uuid import UUIDType

from ..db import Base


class User(Base):
    __tablename__ = "user"

    id = Column("id", UUIDType(), primary_key=True, default=uuid.uuid4)
    email = Column("email", String(255), nullable=False)
    password = Column("password", String(75), nullable=False)
    first_name = Column("first_name", String(255), nullable=False)
    last_name = Column("last_name", String(255), nullable=False)
