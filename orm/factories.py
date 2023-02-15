from typing import Dict, Type

from .repository import SARepository
from services.user.repository import UserRepository


repository_registry: Dict[str, Type[SARepository]] = {
    "user": UserRepository,
}


def repo_factory(name: str):
    return repository_registry[name]
