from adapters import convert_schema_to_model, convert_model_to_schema
from .orm.conftest import UserSchema, UserModel


def test_convert_model_to_schema():
    model = UserModel(username="andrey", password="secret")
    schema = convert_model_to_schema(model, UserSchema)
    assert isinstance(schema, UserSchema)
    assert schema.username == "andrey"
    assert schema.password == "secret"


def test_convert_schema_to_model():
    schema = UserSchema(username="andrey", password="secret")
    model = convert_schema_to_model(schema, UserModel)

    assert isinstance(model, UserModel)
    assert model.username == "andrey"
    assert model.password == "secret"
