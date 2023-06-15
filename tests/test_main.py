from typing import Literal

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import pwd_context, AuthJWTSettings
from src.exceptions import EmailAlreadyExistsError
from src.models import User
import sqlalchemy as sa

from src.utils import verify_password
from tests.conftest import PAYLOAD_DATA

pytestmark = pytest.mark.asyncio


async def test_login_for_access_token(client: AsyncClient, session: AsyncSession):
    login_data = {
        "username": "testmail@example.com",
        "password": "test_password"
    }

    response = await client.post(f'/login/', data=login_data)
    assert response.status_code == 200
    assert response.json()['token_type'] == 'bearer'

    jwt_token = response.json()['access_token']
    jwt_token_decoded = jwt.decode(jwt_token, AuthJWTSettings().authjwt_secret_key, "HS256")

    result = await session.execute(sa.select(User).where(User.email == login_data['username']))
    user = result.scalar_one()
    assert jwt_token_decoded['sub'] == str(user.email)


async def test_login_for_access_token_wrong_data(client: AsyncClient):
    login_data = {}
    response = await client.post(f'/login/', data=login_data)
    assert response.status_code == 422

    login_data = {"username": "test"}
    response = await client.post(f'/login/', data=login_data)
    assert response.status_code == 422

    login_data = {
        "username": "testmail@example.com",
        "password": "wrongpass"
    }
    response = await client.post(f'/login/', data=login_data)
    assert response.status_code == 401
    assert ('www-authenticate', 'Bearer') in response.headers.items()
    assert response.json()['detail'] == 'Incorrect email or password'

    login_data = {
        "username": "   ",
        "password": "wrongpass"
    }
    response = await client.post(f'/login/', data=login_data)
    assert response.status_code == 401


async def test_get_current_user(client: AsyncClient, auth_headers_superuser: tuple[Literal["Authorization"], str]):
    response = await client.get(f'/users/me/', headers=[auth_headers_superuser])
    assert response.status_code == 200
    response_user_data = response.json()
    preload_user_data = PAYLOAD_DATA['user_2']
    assert len(response_user_data) == len(PAYLOAD_DATA['user_1'].items())
    assert response_user_data['email'] == preload_user_data['email']
    assert response_user_data['is_active'] is True


async def test_get_current_user_wrong_data(client: AsyncClient):
    response = await client.get(f'/users/me/')
    assert response.status_code == 401

    response = await client.get(f'/users/me/', headers=[("Authorization", "test")])
    assert response.status_code == 401


async def test_get_certain_user(
        client: AsyncClient,
        auth_headers_superuser: tuple[Literal["Authorization"], str],
        auth_headers_ordinary_user: tuple[Literal["Authorization"], str]
):
    response = await client.get(f'/users/2/', headers=[auth_headers_superuser])
    assert response.status_code == 200
    response_user_data = response.json()
    preload_user_data = PAYLOAD_DATA['user_2']
    assert len(response_user_data) == len(PAYLOAD_DATA["user_1"].items())
    assert response_user_data['id'] == 2
    assert response_user_data['email'] == preload_user_data['email']
    assert response_user_data['is_active'] is True

    response = await client.get(f'/users/2/', headers=[auth_headers_ordinary_user])
    assert response.status_code == 200
    response_user_data = response.json()
    assert len(response_user_data) == 6
    assert response_user_data['id'] == 2


async def test_get_certain_user_wrong_data(
        client: AsyncClient,
        auth_headers_superuser: tuple[Literal["Authorization"], str],
        auth_headers_ordinary_user: tuple[Literal["Authorization"], str]
):
    response = await client.get(f'/users/1/', headers=[auth_headers_ordinary_user])
    assert response.status_code == 403

    response = await client.get(f'/users/1/')
    assert response.status_code == 401

    response = await client.get(f'/users/1/', headers=[('Authorization', 'test')])
    assert response.status_code == 401

    response = await client.get(f'/users/999/', headers=[auth_headers_superuser])
    assert response.status_code == 403

    response = await client.get(f'/users/test/', headers=[auth_headers_superuser])
    assert response.status_code == 422


async def test_create_user(client: AsyncClient, session: AsyncSession):
    user_data = {
        "email": "test123@example.com",
        "password1": "test_password",
        "password2": "test_password",
    }
    response = await client.post(
        f'/users/',
        json=user_data,
    )
    response_user_data = response.json()
    assert len(response_user_data) == 6
    assert response_user_data['email'] == user_data['email']
    assert response_user_data['is_active'] is True

    result = await session.execute(sa.select(User).where(User.id == response_user_data['id']))
    user = result.scalar_one_or_none()
    assert pwd_context.verify(user_data['password1'], user.hashed_password)


async def test_create_user_wrong_data(client: AsyncClient):
    user_data = {
        "email": "wrong_email"
    }
    response = await client.post(f'/users/', json=user_data)
    assert response.status_code == 422

    user_data = {
        "email": "test@example.com",
        "password1": "correct_password",
        "password2": "incorrect_password"
    }
    response = await client.post(f'/users/', json=user_data)
    assert response.status_code == 422

    user_data = {
        "password1": "correct_password",
        "password2": "correct_password"
    }
    response = await client.post(f'/users/', json=user_data)
    assert response.status_code == 422

    user_data = {
        "email": "test@example.com",
        "password": "lol"
    }
    response = await client.post(f'/users/', json=user_data)
    assert response.status_code == 422

    user_data = {
        "email": "test@example.com",
        "password1": "incorrect_password",
        "password2": "incorrect_password"
    }
    response = await client.post(f'/users/', json=user_data)
    assert response.status_code == 400
    assert response.json()['detail'] == EmailAlreadyExistsError(user_data['email']).detail


async def test_patch_user(
        client: AsyncClient,
        auth_headers_superuser: tuple[Literal["Authorization"], str],
        session: AsyncSession
):
    data_to_update = {
        "password": "test_test"
    }
    response = await client.patch('/users/2/', json=data_to_update, headers=[auth_headers_superuser])
    assert response.status_code == 200

    result = await session.execute(sa.select(User).where(User.id == response.json()["id"]))
    user = result.scalar_one_or_none()
    assert verify_password(data_to_update["password"], user.hashed_password)
