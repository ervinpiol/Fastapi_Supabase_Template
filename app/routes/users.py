from fastapi import APIRouter
from app.core.dependencies import CurrentUser, CurrentUserAsync, DBSession

router = APIRouter(tags=["user"])


@router.get("/users/me")
async def read_users_me(current_user: CurrentUser):
    """Synchronous route with auth"""
    return current_user


@router.get("/users/me/async")
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