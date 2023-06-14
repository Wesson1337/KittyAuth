import os

from passlib.context import CryptContext
from pydantic import BaseSettings, BaseModel

# API prefix for whole app.
API_PREFIX_V1 = "/api/v1"

# Debug setting. If False, hides all logging info from SQLAlchemy.
DEBUG = bool(int(os.getenv("DEBUG") or 1))

# Database settings.
DB_DIALECT = "postgresql"
DB_DRIVER = "asyncpg"
DB_USER = os.getenv('DB_USER') or "postgres"
DB_PASSWORD = os.getenv('DB_PASSWORD') or "password"
DB_NAME = os.getenv("DB_NAME") or "postgres"
DB_HOST = os.getenv('DB_HOST') or "localhost"
DB_PORT = os.getenv('DB_DEV_PORT') or "5432"
DB_TEST_HOST = os.getenv("DB_TEST_HOST") or "localhost"
DB_TEST_PORT = os.getenv("DB_TEST_PORT") or "8001"


DATABASE_URL = f"{DB_DIALECT}+{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
TEST_DATABASE_URL = f"{DB_DIALECT}+{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_TEST_HOST}:{DB_TEST_PORT}/{DB_NAME}"


# Settings for fastapi-jwt-auth library.
class AuthJWTSettings(BaseModel):
    authjwt_secret_key: str = os.getenv("AUTHJWT_SECRET_KEY")
    authjwt_access_token_expires: int = 60 * 60 * 12  # 12 hours


# Crypt settings.
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
