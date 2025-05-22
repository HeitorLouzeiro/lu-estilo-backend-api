from pydantic import BaseModel, EmailStr
from typing import Optional
from src.models.user import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.USER


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: str
    password: str
