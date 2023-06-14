
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from . import config, database
from .dependencies import get_async_session, get_current_active_user
from .exceptions import IncorrectEmailOrPasswordError, UserNotFoundError, NotSuperUserError, EmailAlreadyExistsError
from .models import User
from .schemas import UserSchemaOut, UserSchemaRegistration, UserSchemaLogin, UserSchemaPatch
from .services import UserService


app = FastAPI()


@app.on_event("startup")
async def init_models():
    await database.init_db()


@AuthJWT.load_config
def get_config():
    return config.AuthJWTSettings()


@app.post('/login')
async def login(
        user: OAuth2PasswordRequestForm = Depends(),
        authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_async_session)
) -> dict:
    """Route to get access token, accepts login and password"""
    user = await UserService(session).authenticate_user(user.username, user.password)
    if not user:
        raise IncorrectEmailOrPasswordError()
    access_token = authorize.create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get('/users/me', response_model=UserSchemaOut)
async def get_current_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Route to get current user by JWT token in header"""
    return current_user


@app.get('/users/{user_id}', response_model=UserSchemaOut)
async def get_certain_user(
        user_id: int,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_async_session),
) -> User:
    """Route to get certain user, even if users are different"""
    if user_id == current_user.id:  # check not to re-pull the current user
        return current_user

    if not current_user.is_superuser:
        raise NotSuperUserError()

    user = await UserService(session).get_user(id=user_id)
    if user is None:
        raise UserNotFoundError(user_id)
    return user


@app.post('/users', status_code=status.HTTP_201_CREATED, response_model=UserSchemaOut)
async def create_new_user(
        user_data: UserSchemaRegistration,
        session: AsyncSession = Depends(get_async_session),
) -> User:
    """Route to create new user"""
    user_with_entered_email = await UserService(session).get_user(email=user_data.email)
    if user_with_entered_email is not None:
        raise EmailAlreadyExistsError(user_data.email)

    new_user = await UserService(session).create_user(user_data)
    return new_user


@app.patch('/users/{user_id}', response_model=UserSchemaOut)
async def patch_user(
        user_id: int,
        user_data: UserSchemaPatch,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_async_session)
) -> User:
    """Route to partially change user"""
    if user_id == current_user.id:  # check not to re-pull the current user
        updated_user = await UserService(session).patch_user(stored_user=current_user, user_data=user_data)
        return updated_user

    if not current_user.is_superuser:
        raise NotSuperUserError()

    stored_user = await UserService(session).get_user(id=user_id)
    if stored_user is None:
        raise UserNotFoundError(user_id)

    updated_user = await UserService(session).patch_user(stored_user=stored_user, user_data=user_data)
    return updated_user
