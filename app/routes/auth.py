from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.services.user_service import create_user, get_user_by_email
from app.core.dependencies import DBSession, SupabaseClient
from app.schemas.users import (
    AuthResponse,
    LoginInput,
    Message,
    NewPassword,
    PasswordResetRequest,
    ResendVerificationInput,
    UserCreate,
    UserPublic,
    UserRegister,
    VerifyEmailInput,
)

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"],
)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(
    payload: UserRegister,
    db: DBSession,
    supabase: SupabaseClient,
):
    # Check for existing user in local DB
    existing = get_user_by_email(session=db, email=payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create user in Supabase Auth
    try:
        auth_resp = supabase.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
                "options": {"data": {"full_name": payload.full_name}},
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Supabase signup failed: {exc}",
        )

    supabase_user_id = getattr(auth_resp.user, "id", None) if auth_resp else None

    # Create local DB record (store hashed password)
    db_user = create_user(
        session=db,
        user_create=UserCreate(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
        ),
        user_id=supabase_user_id,
    )

    # If email confirmation is required, Supabase returns session=None
    if not auth_resp or not auth_resp.session:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Signup successful. Please verify your email before logging in.",
        )

    access_token = auth_resp.session.access_token
    return AuthResponse(
        access_token=access_token,
        user=UserPublic.model_validate(db_user),
    )


@router.post("/login", response_model=AuthResponse)
def login(
    credentials: LoginInput,
    db: DBSession,
    supabase: SupabaseClient,
):
    try:
        auth_resp = supabase.auth.sign_in_with_password(
            {"email": credentials.email, "password": credentials.password}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not auth_resp or not auth_resp.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to retrieve access token",
        )

    # Ensure local DB user exists (create on first login)
    user = get_user_by_email(session=db, email=credentials.email)
    if not user:
        user = create_user(
            session=db,
            user_create=UserCreate(
                email=credentials.email,
                password=credentials.password,
                full_name=getattr(auth_resp.user, "user_metadata", {}).get(
                    "full_name", None
                )
                if auth_resp and auth_resp.user and auth_resp.user.user_metadata
                else None,
            ),
            user_id=getattr(auth_resp.user, "id", None) if auth_resp else None,
        )

    return AuthResponse(
        access_token=auth_resp.session.access_token,
        user=UserPublic.model_validate(user),
    )


@router.post("/verify-email", response_model=AuthResponse)
def verify_email(
    payload: VerifyEmailInput,
    db: DBSession,
    supabase: SupabaseClient,
):
    try:
        auth_resp = supabase.auth.verify_otp(
            {"email": payload.email, "token": payload.token, "type": payload.type}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email verification failed: {exc}",
        )
    if not auth_resp or not auth_resp.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to retrieve access token after verification",
        )

    user = get_user_by_email(session=db, email=payload.email)
    if not user:
        user = create_user(
            session=db,
            user_create=UserCreate(
                email=payload.email,
                password=payload.token,  # placeholder; Supabase password already set
                full_name=getattr(auth_resp.user, "user_metadata", {}).get(
                    "full_name", None
                )
                if auth_resp and auth_resp.user and auth_resp.user.user_metadata
                else None,
            ),
            user_id=getattr(auth_resp.user, "id", None) if auth_resp else None,
        )

    return AuthResponse(
        access_token=auth_resp.session.access_token,
        user=UserPublic.model_validate(user),
    )


@router.post("/resend-verification", response_model=Message)
def resend_verification(
    payload: ResendVerificationInput,
    supabase: SupabaseClient,
):
    try:
        supabase.auth.resend({"email": payload.email, "type": payload.type})
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resend verification failed: {exc}",
        )
    return Message(message="Verification email sent if the account exists.")


@router.post("/reset-password", response_model=Message)
def reset_password_request(
    payload: PasswordResetRequest,
    supabase: SupabaseClient,
):
    try:
        supabase.auth.reset_password_email(payload.email)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password reset request failed: {exc}",
        )
    return Message(message="If the email exists, a reset link has been sent.")


@router.post("/reset-password/confirm", response_model=Message)
def reset_password_confirm(
    payload: NewPassword,
    supabase: SupabaseClient,
):
    try:
        # Supabase expects the reset token sent in the email link
        supabase.auth.update_user(
            {"password": payload.new_password},
            access_token=payload.token,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password reset confirmation failed: {exc}",
        )
    return Message(message="Password updated successfully.")