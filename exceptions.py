from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from orm.repository import RepositoryException


def register_exceptions(app: FastAPI):
    app.exception_handler(RepositoryException)(repository_exception_handler)


async def repository_exception_handler(request: Request, exc: RepositoryException):
    return JSONResponse(
        status_code=422,
        content={"message": f"An error occured: {exc}"},
    )
