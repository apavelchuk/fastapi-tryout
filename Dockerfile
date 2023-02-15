FROM python:3.9-alpine

ENV DB_CONNECT="postgresql+asyncpg://fastapi:fastapi@fastapi-db/fastapi"

RUN apk update && apk add postgresql-dev python3-dev gcc musl-dev linux-headers libc-dev g++

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

COPY --chown=bitposter:bitposter . /app

WORKDIR /app
CMD ["uvicorn", "--host", "0.0.0.0", "app:app", "--reload"]
