from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.models.order import OrderStatus
from src.schemas.client import ClientResponse


class OrderItemBase(BaseModel):
    product_id: int = Field(..., description="ID do produto", example=1)
    quantity: int = Field(..., gt=0, description="Quantidade do produto", example=2)


class OrderItemCreate(OrderItemBase):
    class Config:
        schema_extra = {
            "example": {
                "product_id": 1,
                "quantity": 2
            }
        }


class OrderItemResponse(OrderItemBase):
    unit_price: float = Field(..., description="Preço unitário no momento do pedido", example=89.90)

    class Config:
        orm_mode = True
        from_attributes = True
        schema_extra = {
            "example": {
                "product_id": 1,
                "quantity": 2,
                "unit_price": 89.90
            }
        }


class OrderBase(BaseModel):
    client_id: int = Field(..., description="ID do cliente", example=1)
    status: Optional[OrderStatus] = Field(OrderStatus.PENDING, description="Status do pedido", example="pending")


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., description="Lista de itens do pedido")

    class Config:
        schema_extra = {
            "example": {
                "client_id": 1,
                "status": "pending",
                "items": [
                    {
                        "product_id": 1,
                        "quantity": 2
                    },
                    {
                        "product_id": 2,
                        "quantity": 1
                    }
                ]
            }
        }


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = Field(None, description="Novo status do pedido", example="confirmed")

    class Config:
        schema_extra = {
            "example": {
                "status": "confirmed"
            }
        }


class OrderResponse(OrderBase):
    id: int = Field(..., description="ID único do pedido", example=1)
    total_amount: float = Field(..., description="Valor total do pedido", example=259.70)
    created_at: datetime = Field(..., description="Data de criação", example="2024-01-15T10:30:00")
    updated_at: datetime = Field(..., description="Data da última atualização", example="2024-01-20T14:45:00")
    items: List[OrderItemResponse] = Field(..., description="Lista de itens do pedido")
    client: Optional[ClientResponse] = Field(None, description="Dados do cliente")

    class Config:
        orm_mode = True
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "client_id": 1,
                "status": "pending",
                "total_amount": 259.70,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-20T14:45:00",
                "items": [
                    {
                        "product_id": 1,
                        "quantity": 2,
                        "unit_price": 89.90
                    },
                    {
                        "product_id": 2,
                        "quantity": 1,
                        "unit_price": 79.90
                    }
                ],
                "client": {
                    "id": 1,
                    "name": "Maria Silva Santos",
                    "email": "maria@email.com",
                    "cpf": "12345678901",
                    "phone": "(11) 99999-8888",
                    "address": "Rua das Flores, 123, São Paulo - SP",
                    "created_at": "2024-01-10T08:00:00",
                    "updated_at": "2024-01-10T08:00:00"
                }
            }
        }


class OrderList(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    size: int
