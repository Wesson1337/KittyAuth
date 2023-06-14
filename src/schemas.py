import datetime
from typing import Optional

from pydantic import EmailStr, constr, BaseModel, validator


class BaseORMSchema(BaseModel):
    class Config:
        orm_mode = True


class UserSchemaIn(BaseORMSchema):
    email: EmailStr
    password1: constr(min_length=6, max_length=24)
    password2: constr(min_length=6, max_length=24)

    @validator("password2")
    def passwords_match(cls, v, values):
        if "password1" in values and v != values['password1']:
            raise ValueError("Пароли не совпадают")

    class Config:
        orm_mode = True


class UserSchemaPatch(BaseORMSchema):
    email: Optional[EmailStr]
    password: Optional[constr(min_length=6, max_length=24)]
    is_active: Optional[bool]
    is_superuser: Optional[bool]


class UserSchemaOut(BaseORMSchema):
    id: int
    email: str
    profile_picture_url: str
    is_active: bool
    created_at: datetime.datetime
