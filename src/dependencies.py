from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from sqlalchemy.ext.asyncio import AsyncSession
from . import database
from .exceptions import CredentialsError, InactiveUserError
from .models import User
from .schemas import TokenSubject
from .services import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_async_session() -> AsyncSession:
    async with database.async_session() as session:
        yield session


async def get_current_user(
        authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_async_session),
        token=Depends(oauth2_scheme)  # Using this dependency for swagger ui
) -> User:
    """Dependency that returns user from JWT token in request header, make routes protected in swagger ui"""
    try:
        authorize.jwt_required()
        email = authorize.get_jwt_subject()
        TokenSubject(email=email)
    except AuthJWTException:
        raise CredentialsError()

    user = await UserService(session).get_user(email=email)
    if user is None:
        raise CredentialsError()

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Checks if user is active"""
    if not current_user.is_active:
        raise InactiveUserError()
    return current_user

