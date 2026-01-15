import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate


def create_user(
    *,
    session: Session,
    user_create: UserCreate,
    user_id: uuid.UUID | None = None,
) -> User:
    """Create a user with hashed password."""

    user_data = user_create.model_dump(exclude={"password"})

    if user_id is not None:
        user_data["id"] = user_id

    db_obj = User(
        **user_data,
        hashed_password=get_password_hash(user_create.password),
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    """Update user fields, hashing password when provided."""

    user_data = user_in.model_dump(exclude_unset=True)

    if "password" in user_data:
        password = user_data.pop("password")
        db_user.hashed_password = get_password_hash(password)

    for field, value in user_data.items():
        setattr(db_user, field, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.scalars(statement).first()


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
