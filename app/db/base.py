"""Declarative base and model aggregation for Alembic autogeneration."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models here so Alembic can discover them via Base.metadata
from app.models import users  # noqa: E402,F401
