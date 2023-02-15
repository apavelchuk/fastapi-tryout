# Fast API Tryout

The project is a tryout of FastAPI lib.
It also makes use of Docker, uvicorn, Postgres/asyncpg, SQLAlchemy, Alembic for migrations and some code quality tools (flake8/black/mypy).
A single User entity is available at the moment.

## Docker-compose

You can leverage existing Docker config provided. In includes database and the API itself:
```
docker-compose up
```
See `docker-compose.yaml` for more info.

Now you have to be able to access `localhost:8000/docs` and `/users/` endpoints.


## Testing

```
coverage run -m pytest
```
