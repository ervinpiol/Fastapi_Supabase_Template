from fastapi import APIRouter
from app.core.config import settings
from app.core.dependencies import CurrentUser, CurrentUserAsync, DBSession

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/users",
    tags=["user"],
)


@router.get("/me")
async def read_users_me(current_user: CurrentUser):
    """Synchronous route with auth"""
    return current_user


@router.get("/me/async")
async def read_users_me_async(current_user: CurrentUserAsync):
    """Fully async route with auth"""
    return current_user


@router.get("/protected")
async def protected_route(
    current_user: CurrentUser,
    db: DBSession,
):
    """Example protected route with database access"""
    # Use db for queries
    return {"message": "Protected data", "user": current_user.email}