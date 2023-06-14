import aiohttp

from src.config import pwd_context


def get_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_random_kitty_picture_id():
    """Gets random kitty id from cataas.com api with 200px width and height"""
    async with aiohttp.ClientSession() as session:
        async with session.get(
                "https://cataas.com/cat",
                params=[("width", 200), ("height", 200), ("json", True)]
        ) as response:
            data: dict = await response.json()
            return data.get("_id")

