from typing import Type

import aiohttp

from src.config import pwd_context
from src.database import Base


def get_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_random_kitty_picture_id():
    """Gets random kitty id from cataas.com api with 200px width and height"""
    async with aiohttp.ClientSession() as session:
        async with session.get(
                "https://cataas.com/cat",
                params=[("width", 200), ("height", 200), ("json", "true")]
        ) as response:
            data: dict = await response.json()
            return data.get("_id")


async def update_sql_entity(sql_entity: Type[Base], data_to_update: dict) -> Type[Base]:
    """Updates sql entity by dict with sql entity attribute as a key, returns sql entity with updated attributes"""
    if not data_to_update:
        raise ValueError("No data to update entity")

    for key, value in data_to_update.items():
        if key not in dir(sql_entity):
            raise ValueError(f"The attribute {key} is missing from the model {sql_entity.__tablename__}")

        if key is not None and value is not None:
            setattr(sql_entity, key, value)

    return sql_entity
