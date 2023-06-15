import asyncio
from typing import Generator, Callable, Literal

import pytest_asyncio
from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import TEST_DATABASE_URL, pwd_context
from src.database import Base
from src.dependencies import get_async_session
from src.main import app
from src.models import User

PAYLOAD_DATA = {
    "user_1": {
        "email": "testmail@example.com",
        "hashed_password": pwd_context.hash("test_password"),
        "profile_picture_id": "Z0aeZsdukWvVItTO",
        "profile_picture_url": "https://cataas.com/cat/Z0aeZsdukWvVItTO?width=200&height=200",
        "is_superuser": True,
        "is_active": True,

    },
    "user_2": {
        "email": "test@example.com",
        "hashed_password": pwd_context.hash("test_password"),
        "profile_picture_id": "Z0aeZsdukWvVItTO",
        "profile_picture_url": "https://cataas.com/cat/Z0aeZsdukWvVItTO?width=200&height=200",
        "is_superuser": False,
        "is_active": True
    },
    "user_3": {
        "email": "inactiveuser@example.com",
        "hashed_password": pwd_context.hash("test_password"),
        "profile_picture_id": "19Ykh6wwZdgIEL2D",
        "profile_picture_url": "https://cataas.com/cat/19Ykh6wwZdgIEL2D?width=200&height=200",
        "is_superuser": False,
        "is_active": False
    }
}


@pytest_asyncio.fixture(scope="function")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncEngine:
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session(db_engine: AsyncEngine) -> AsyncSession:
    async_session = sessionmaker(bind=db_engine, expire_on_commit=False, class_=AsyncSession)
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        async with async_session(bind=conn) as session:
            yield session
            await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def seed_db(session: AsyncSession) -> None:
    for data in PAYLOAD_DATA.values():
        session.add(User(**data))
    await session.commit()


@pytest_asyncio.fixture(scope="function")
def override_get_async_session(session: AsyncSession) -> Callable:
    async def _override_get_async_session():
        yield session

    return _override_get_async_session


@pytest_asyncio.fixture(scope="function")
def test_app(override_get_async_session: Callable) -> FastAPI:
    app.dependency_overrides[get_async_session] = override_get_async_session
    return app


@pytest_asyncio.fixture(scope="function")
async def client(seed_db, test_app: FastAPI) -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def superuser_encoded_jwt_token(seed_db) -> str:
    user_email = "test@example.com"
    encoded_token = AuthJWT().create_access_token(subject=user_email, algorithm="HS256",
                                                  expires_time=60 * 60 * 3)
    return encoded_token


@pytest_asyncio.fixture(scope="function")
async def auth_headers_superuser(superuser_encoded_jwt_token: str) -> tuple[Literal["Authorization"], str]:
    auth_headers = ('Authorization', f'Bearer {superuser_encoded_jwt_token}')
    return auth_headers


@pytest_asyncio.fixture(scope="function")
async def ordinary_user_encoded_jwt_token(seed_db) -> str:
    user_email = "test@example.com"
    encoded_token = AuthJWT().create_access_token(subject=user_email, algorithm="HS256",
                                                  expires_time=60 * 60 * 3)
    return encoded_token


@pytest_asyncio.fixture(scope="function")
async def auth_headers_ordinary_user(ordinary_user_encoded_jwt_token: str) -> tuple[Literal["Authorization"], str]:
    auth_headers = ('Authorization', f'Bearer {ordinary_user_encoded_jwt_token}')
    return auth_headers
