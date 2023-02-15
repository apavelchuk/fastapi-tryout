from fastapi import FastAPI

from services.user.api import router as user_router
from exceptions import register_exceptions

app = FastAPI()

app.include_router(user_router, prefix="/users")
register_exceptions(app)
