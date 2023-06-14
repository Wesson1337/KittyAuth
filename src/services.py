from typing import Optional

import sqlalchemy as sa
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.schemas import UserSchemaRegistration, UserSchemaPatch
from . import utils
from .utils import get_random_kitty_picture_id


class UserService:
    """Class to getting or changing user data in database"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, id: Optional[int] = None, email: Optional[EmailStr] = None) -> User | None:
        """Gets user by id or email. At least one argument must be filled"""
        if id is None and email is None:
            raise ValueError("At least one argument must be filled")

        query = sa.select(User)
        if id is not None:
            query = query.where(User.id == id)
        if email is not None:
            query = query.where(User.email == email)

        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def authenticate_user(self, email: EmailStr, password: str) -> User | None:
        """Checks if user's data matches the entered data, returns user if successful"""
        user = await self.get_user(email=email)
        if user is None:
            return
        if utils.verify_password(password, user.hashed_password):
            return user

    async def create_user(self, user_data: UserSchemaRegistration) -> User:
        """Creates new user, gets profile picture from api"""
        new_user = user_data.transform_data_to_save()  # Attributes of profile_picture are missed
        profile_picture_id = await get_random_kitty_picture_id()
        new_user.update({
            "profile_picture_id": profile_picture_id,
            "profile_picture_url": f"https://catass.com/cat/{profile_picture_id}?width=200&height=200"
        })
        new_user = User(**new_user)
        self.session.add(new_user)
        await self.session.commit()

        return new_user

    async def patch_user(self, stored_user: User, user_data: UserSchemaPatch) -> User | None:
        """Partially changes user data"""
        user_data: dict = user_data.dict(exclude_unset=True)
        if not user_data:
            raise ValueError("No data to update entity")

        updated_user = await utils.update_sql_entity(stored_user, user_data)
        await self.session.commit()

        return updated_user




