from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.models.order import OrderStatus
from src.schemas.client import ClientResponse


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    unit_price: float

    class Config:
        orm_mode = True
        from_attributes = True


class OrderBase(BaseModel):
    client_id: int
    status: Optional[OrderStatus] = OrderStatus.PENDING


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None


class OrderResponse(OrderBase):
    id: int
    total_amount: float
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]
    client: Optional[ClientResponse] = None

    class Config:
        orm_mode = True
        from_attributes = True


class OrderList(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    size: int
