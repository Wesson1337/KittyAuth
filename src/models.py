from sqlalchemy import func
from . import database
import sqlalchemy as sa


class User(database.Base):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    email = sa.Column(sa.String(255), unique=True, nullable=False)
    profile_picture_id = sa.Column(sa.String, nullable=False)
    profile_picture_url = sa.Column(sa.String, nullable=False)
    hashed_password = sa.Column(sa.String(32), nullable=False)
    is_active = sa.Column(sa.Boolean, default=True, nullable=False)
    is_superuser = sa.Column(sa.Boolean, default=False, nullable=False)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now(), nullable=False)
