import pytest

from src.config import pwd_context
from src.models import User
from src.utils import update_sql_entity, get_password_hash, verify_password


@pytest.mark.asyncio
async def test_update_sql_entity():
    sql_entity = User(
        email="lol@email.com"
    )
    data_to_update = {
        "email": "test@email.com",
        "hashed_password": "testvalue"
    }
    updated_sql_entity = await update_sql_entity(sql_entity, data_to_update)
    assert updated_sql_entity.email == data_to_update['email']
    assert updated_sql_entity.hashed_password == data_to_update['hashed_password']


@pytest.mark.asyncio
async def test_update_sql_entity_wrong_data():
    sql_entity = User(
        email="lol@email.com"
    )

    data_to_update = {
        "incorrect_key": "incorrect_value"
    }
    with pytest.raises(ValueError):
        await update_sql_entity(sql_entity, data_to_update)

    data_to_update = {}
    with pytest.raises(ValueError):
        await update_sql_entity(sql_entity, data_to_update)


def test_get_password_hash():
    plain_password = 'test_password'
    hashed_password = get_password_hash(plain_password)
    assert pwd_context.verify(plain_password, hashed_password)
    assert not pwd_context.verify('test', hashed_password)


def test_verify_password():
    plain_password = 'test_password'
    hashed_password = pwd_context.hash(plain_password)
    assert verify_password(plain_password, hashed_password)
    assert not verify_password('test', hashed_password)
