from .domain_entity import DomainEntity


class User(DomainEntity):
    email: str
    password: str
    first_name: str
    last_name: str
