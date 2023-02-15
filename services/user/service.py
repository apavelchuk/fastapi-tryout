import hashlib

from pydantic import BaseModel
from typing import Type

from domain.user import User
from orm.repository import Repository


def hash_password(password: str):
    return hashlib.sha512(password.encode("utf-8")).hexdigest()[:75]


async def create_user(repo: Repository, user: User, response_schema: Type[BaseModel]) -> User:
    user.password = hash_password(user.password)
    user = await repo.create(user, response_schema)
    return user
