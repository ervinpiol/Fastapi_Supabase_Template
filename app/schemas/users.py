from pydantic import BaseModel, EmailStr, ConfigDict
import uuid
from typing import List, Optional, Literal

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None

class UserPublic(UserBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True) # Allows reading SQLAlchemy objects

class UsersPublic(BaseModel):
    data: List[UserPublic]
    count: int

# --- Auth & Utility Schemas ---
class LoginInput(BaseModel):
    email: EmailStr
    password: str
 
class PasswordResetRequest(BaseModel):
    email: EmailStr
 
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
 
class TokenPayload(BaseModel):
    sub: Optional[str] = None
 
class NewPassword(BaseModel):
    token: str
    new_password: str
 
class Message(BaseModel):
    message: str
 
class VerifyEmailInput(BaseModel):
    email: EmailStr
    token: str
    type: Literal["email", "signup", "magiclink", "recovery", "email_change"] = "email"
 
class ResendVerificationInput(BaseModel):
    email: EmailStr
    type: Literal["signup", "email_change"] = "signup"
 
class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic