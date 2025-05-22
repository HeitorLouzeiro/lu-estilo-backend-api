from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class ClientBase(BaseModel):
    name: str
    email: EmailStr
    cpf: str = Field(..., min_length=11, max_length=11)
    phone: Optional[str] = None
    address: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ClientList(BaseModel):
    items: List[ClientResponse]
    total: int
    page: int
    size: int
