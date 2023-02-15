from orm.repository import SARepository
from orm.user import models


class UserRepository(SARepository):
    model = models.User
