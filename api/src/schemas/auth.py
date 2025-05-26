from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from src.models.user import UserRole


class Token(BaseModel):
    access_token: str = Field(..., description="Token JWT de acesso", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(..., description="Tipo do token", example="bearer")

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2FvIiwiZXhwIjoxNjM0NzQ3MjAwfQ.example",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str = Field(..., description="Nome de usuário único", example="joao_silva", min_length=3, max_length=50)
    email: EmailStr = Field(..., description="E-mail do usuário", example="joao@email.com")


class UserCreate(UserBase):
    password: str = Field(..., description="Senha do usuário", example="senha123", min_length=6)
    role: Optional[UserRole] = Field(UserRole.USER, description="Papel do usuário no sistema", example="user")

    class Config:
        schema_extra = {
            "example": {
                "username": "joao_silva",
                "email": "joao@email.com",
                "password": "senha123",
                "role": "user"
            }
        }


class UserResponse(UserBase):
    id: int = Field(..., description="ID único do usuário", example=1)
    role: UserRole = Field(..., description="Papel do usuário", example="user")
    is_active: bool = Field(..., description="Status ativo do usuário", example=True)

    class Config:
        orm_mode = True
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "joao_silva",
                "email": "joao@email.com",
                "role": "user",
                "is_active": True
            }
        }


class UserLogin(BaseModel):
    username: str = Field(..., description="Nome de usuário", example="joao_silva")
    password: str = Field(..., description="Senha do usuário", example="senha123")

    class Config:
        schema_extra = {
            "example": {
                "username": "joao_silva",
                "password": "senha123"
            }
        }
