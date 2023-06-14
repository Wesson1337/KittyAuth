import datetime
from typing import Optional

from pydantic import EmailStr, constr, BaseModel, validator

from . import utils


class UserSchemaLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=6, max_length=24)


class UserSchemaRegistration(BaseModel):
    email: EmailStr
    password1: constr(min_length=6, max_length=24)
    password2: constr(min_length=6, max_length=24)

    @validator("password2")
    def passwords_match(cls, v, values):
        if "password1" in values and v != values['password1']:
            raise ValueError("Passwords do not match")

    def transform_data_to_save(self) -> dict:
        """Transforms into a dictionary with attributes of the ORM user model, except profile_picture_id"""
        user: dict = self.dict()
        hashed_password = utils.get_password_hash(self.password1)
        del user["password1"]
        del user["password2"]
        user.update({"hashed_password": hashed_password})
        return user


class UserSchemaPatch(BaseModel):
    password: Optional[constr(min_length=6, max_length=24)]
    is_active: Optional[bool]


class UserSchemaOut(BaseModel):
    id: int
    email: str
    profile_picture_id: str
    profile_picture_url: str
    is_active: bool
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class TokenSubject(BaseModel):
    email: EmailStr
