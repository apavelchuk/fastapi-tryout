import pytest

from sqlalchemy import select, func, delete

from orm.repository import FilterCondition, FindQueryConfig, FilterOps
from .conftest import UserSchema, UserModel, UserRepo


@pytest.mark.asyncio
async def test_create(db):
    created_user = await UserRepo.create(
        UserSchema(username="andrey", password="secret"),
        UserSchema,
    )
    assert isinstance(created_user, UserSchema)
    assert created_user.id is not None
    res = await db.execute(
        select(func.count())
        .select_from(UserModel)
        .where(UserModel.username == "andrey", UserModel.password == "secret")
    )
    assert res.scalar_one() == 1


@pytest.mark.asyncio
async def test_count(db, users):
    count = await UserRepo.count()
    assert count == 3
    await db.execute(delete(UserModel).where(UserModel.username == "andrey"))
    count = await UserRepo.count()
    assert count == 2


@pytest.mark.asyncio
async def test_update_by_id(users):
    user = await UserRepo.update_by_id(users["andrey"].id, values={"password": "newsecret"}, response_schema=UserSchema)
    assert isinstance(user, UserSchema)
    assert user.password == "newsecret"


@pytest.mark.asyncio
async def test_delete(db, users):
    cnt = (await db.execute(select(func.count()).select_from(UserModel))).scalar_one()
    assert cnt == 3
    delete_filter = [FilterCondition(field="username", value="paul")]
    deleted_cnt = await UserRepo.delete(delete_filter)
    assert deleted_cnt == 1
    cnt = await db.execute(
        select(func.count()).select_from(UserModel).where(UserModel.username.in_(["andrey", "andrew"]))
    )
    assert cnt.scalar_one() == 2


@pytest.mark.asyncio
async def test_find(users):
    cnf = FindQueryConfig(
        response_schema=UserSchema,
        conditions=[FilterCondition(field="username", operation=FilterOps.ILIKE, value="ndr")],
    )
    res = {user.username: user async for user in UserRepo.find(cnf)}
    assert len(res) == 2
    assert "andrey" in res
    assert "andrew" in res

    # test limit, offset and order_by
    cnf.limit = 1
    cnf.order_by = ["-username"]
    res = {user.username: user async for user in UserRepo.find(cnf)}
    assert len(res) == 1
    assert "andrey" in res

    cnf.offset = 1
    res = {user.username: user async for user in UserRepo.find(cnf)}
    assert len(res) == 1
    assert "andrew" in res


@pytest.mark.asyncio
async def test_find_one(users):
    user = await UserRepo.find_one(
        conditions=[FilterCondition(field="username", value="andrey")],
        response_schema=UserSchema,
    )
    assert isinstance(user, UserSchema)
    assert user.username == "andrey"

    user = await UserRepo.find_one(
        conditions=[FilterCondition(field="username", value="paul")],
        response_schema=UserSchema,
    )
    assert user.username == "paul"
