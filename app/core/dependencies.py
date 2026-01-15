import logging
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import Client

from app.db.session import get_db, get_async_db
from app.db.supabase import get_supabase_client
from app.models.users import User  # Your User model
from .config import settings

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


# ===== Type Aliases =====
DBSession = Annotated[Session, Depends(get_db)]
AsyncDBSession = Annotated[AsyncSession, Depends(get_async_db)]
SupabaseClient = Annotated[Client, Depends(get_supabase_client)]
AccessToken = Annotated[str, Depends(oauth2_scheme)]


# ===== Auth Dependencies =====
async def get_current_user(
    token: AccessToken,
    db: DBSession,
    supabase: SupabaseClient,
) -> User:
    """
    Validate token with Supabase and get user from database.
    Works with both sync and async routes.
    """
    try:
        # Validate token with Supabase Auth
        auth_response = supabase.auth.get_user(token)
        user_id = auth_response.user.id
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        logger.error(f"User {user_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


async def get_current_user_async(
    token: AccessToken,
    db: AsyncDBSession,
    supabase: SupabaseClient,
) -> User:
    """
    Async version of get_current_user.
    Use this for fully async routes.
    """
    try:
        auth_response = supabase.auth.get_user(token)
        user_id = auth_response.user.id
    except Exception as e:
        logger.error(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Async database query
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        logger.error(f"User {user_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserAsync = Annotated[User, Depends(get_current_user_async)]
