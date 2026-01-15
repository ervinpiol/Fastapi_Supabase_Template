from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"
 
 
def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
 
 
def decode_access_token(token: str) -> str:
    """
    Decode a JWT and return the subject (user id).
    Raises ValueError on invalid/expired tokens.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise ValueError("Token missing subject")
        return str(subject)
    except Exception as exc:
        raise ValueError(f"Invalid token: {exc}")


def _truncate_password(password: str) -> str:
    """Bcrypt only considers first 72 bytes; truncate to avoid errors."""
    return password[:72]
 
 
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_truncate_password(plain_password), hashed_password)
 
 
def get_password_hash(password: str) -> str:
    return pwd_context.hash(_truncate_password(password))