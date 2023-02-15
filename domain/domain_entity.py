from pydantic import BaseModel


class DomainEntity(BaseModel):
    class Config:
        orm_mode = True
