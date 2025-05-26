from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class ClientBase(BaseModel):
    name: str = Field(..., description="Nome completo do cliente", example="Maria Silva Santos", max_length=100)
    email: EmailStr = Field(..., description="E-mail do cliente", example="maria@email.com")
    cpf: str = Field(..., min_length=11, max_length=11, description="CPF do cliente (apenas números)", example="12345678901")
    phone: Optional[str] = Field(None, description="Telefone para contato", example="(11) 99999-8888", max_length=20)
    address: Optional[str] = Field(None, description="Endereço completo", example="Rua das Flores, 123, São Paulo - SP", max_length=200)


class ClientCreate(ClientBase):
    class Config:
        schema_extra = {
            "example": {
                "name": "Maria Silva Santos",
                "email": "maria@email.com",
                "cpf": "12345678901",
                "phone": "(11) 99999-8888",
                "address": "Rua das Flores, 123, São Paulo - SP"
            }
        }


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nome completo do cliente", example="Maria Silva Santos", max_length=100)
    email: Optional[EmailStr] = Field(None, description="E-mail do cliente", example="maria@email.com")
    phone: Optional[str] = Field(None, description="Telefone para contato", example="(11) 99999-8888", max_length=20)
    address: Optional[str] = Field(None, description="Endereço completo", example="Rua das Flores, 123, São Paulo - SP", max_length=200)

    class Config:
        schema_extra = {
            "example": {
                "name": "Maria Silva Santos",
                "email": "maria.nova@email.com",
                "phone": "(11) 88888-7777",
                "address": "Av. Paulista, 456, São Paulo - SP"
            }
        }


class ClientResponse(ClientBase):
    id: int = Field(..., description="ID único do cliente", example=1)
    created_at: datetime = Field(..., description="Data de criação", example="2024-01-15T10:30:00")
    updated_at: datetime = Field(..., description="Data da última atualização", example="2024-01-20T14:45:00")

    class Config:
        orm_mode = True
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Maria Silva Santos",
                "email": "maria@email.com",
                "cpf": "12345678901",
                "phone": "(11) 99999-8888",
                "address": "Rua das Flores, 123, São Paulo - SP",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-20T14:45:00"
            }
        }


class ClientList(BaseModel):
    items: List[ClientResponse]
    total: int
    page: int
    size: int
