from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    description: str
    price: float = Field(..., gt=0)
    barcode: Optional[str] = None
    section: str
    stock: int = Field(..., ge=0)
    expiry_date: Optional[date] = None
    image_urls: Optional[List[str]] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    barcode: Optional[str] = None
    section: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    expiry_date: Optional[date] = None
    image_urls: Optional[List[str]] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class ProductList(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    size: int
