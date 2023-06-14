import asyncio
from typing import Generator, Callable, Literal

import aiohttp
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import TEST_DATABASE_URL
from src.database import Base
from src.dependencies import get_async_session
from src.main import app
from src.models import User

PAYLOAD_DATA = {
    "user_1": {
        "email": "testmail@example.com",
        # plain password = test_password
        "hashed_password": "$2b$12$Ql7XTNhMhDbIEHlYnBxQeOi1MMPS.yxx3cWt4j1FILtJ.VkMubnJy",
        "profile_picture_id": "Z0aeZsdukWvVItTO",
        "profile_picture_url": "https://cataas.com/cat/Z0aeZsdukWvVItTO?width=200&height=200",
        "is_superuser": True,
        "is_active": True,

    },
    "user_2": {
        "email": "test@example.com",
        # plain password = test_password
        "hashed_password": "$2b$12$kYRIvRY4vySCrR10hhZaVuRQCjU.78x2zaGpo2TsuSOjJVoVEBIyG",
        "profile_picture_id": "Z0aeZsdukWvVItTO",
        "profile_picture_url": "https://cataas.com/cat/Z0aeZsdukWvVItTO?width=200&height=200",
        "is_superuser": False,
        "is_active": True
    },
    "user_3": {
        "email": "inactiveuser@example.com",
        # plain password = test_password
        "hashed_password": "$2b$12$kYRIvRY4vySCrR10hhZaVuRQCjU.78x2zaGpo2TsuSOjJVoVEBIyG",
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
async def client(seed_db, test_app: FastAPI, seed_test_redis_from_test_db) -> :
    async with aiohttp.ClientSession(base_url="http://localhost:8000") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def superuser_encoded_jwt_token(seed_db, seed_test_redis_from_test_db) -> str:
    user_email = "test@example.com"
    data_to_encode = {"sub": user_id, "exp": datetime.utcnow() + timedelta(minutes=300)}
    encoded_jwt_token = jwt.encode(data_to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)
    return encoded_jwt_token


@pytest_asyncio.fixture(scope="function")
async def auth_headers_superuser(superuser_encoded_jwt_token: str) -> tuple[Literal["Authorization"], str]:
    auth_headers = ('Authorization', f'Bearer {superuser_encoded_jwt_token}')
    return auth_headers


@pytest_asyncio.fixture(scope="function")
async def ordinary_user_encoded_jwt_token(seed_db, seed_test_redis_from_test_db) -> str:
    user_email = "test@example.com"
    data_to_encode = {"sub": user_email, "exp": datetime.utcnow() + timedelta(minutes=300)}
    encoded_jwt_token = jwt.encode(data_to_encode, JWT_SECRET_KEY, JWT_ALGORITHM)
    return encoded_jwt_token


@pytest_asyncio.fixture(scope="function")
async def auth_headers_ordinary_user(ordinary_user_encoded_jwt_token: str) -> tuple[Literal["Authorization"], str]:
    auth_headers = ('Authorization', f'Bearer {ordinary_user_encoded_jwt_token}')
    return auth_headers