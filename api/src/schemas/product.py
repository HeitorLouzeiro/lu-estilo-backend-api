from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    description: str = Field(..., description="Descrição do produto", example="Vestido Floral Verão", max_length=200)
    price: float = Field(..., gt=0, description="Preço do produto", example=89.90)
    barcode: Optional[str] = Field(None, description="Código de barras", example="7891234567890", max_length=20)
    section: str = Field(..., description="Seção/categoria do produto", example="Roupas Femininas", max_length=50)
    stock: int = Field(..., ge=0, description="Quantidade em estoque", example=15)
    expiry_date: Optional[date] = Field(None, description="Data de validade (se aplicável)", example="2024-12-31")
    image_urls: Optional[List[str]] = Field(None, description="URLs das imagens do produto", example=["https://exemplo.com/imagem1.jpg", "https://exemplo.com/imagem2.jpg"])


class ProductCreate(ProductBase):
    class Config:
        schema_extra = {
            "example": {
                "description": "Vestido Floral Verão",
                "price": 89.90,
                "barcode": "7891234567890",
                "section": "Roupas Femininas",
                "stock": 15,
                "expiry_date": "2024-12-31",
                "image_urls": ["https://exemplo.com/imagem1.jpg"]
            }
        }


class ProductUpdate(BaseModel):
    description: Optional[str] = Field(None, description="Descrição do produto", example="Vestido Floral Verão - Novo", max_length=200)
    price: Optional[float] = Field(None, gt=0, description="Preço do produto", example=79.90)
    barcode: Optional[str] = Field(None, description="Código de barras", example="7891234567890", max_length=20)
    section: Optional[str] = Field(None, description="Seção/categoria do produto", example="Roupas Femininas", max_length=50)
    stock: Optional[int] = Field(None, ge=0, description="Quantidade em estoque", example=20)
    expiry_date: Optional[date] = Field(None, description="Data de validade (se aplicável)", example="2024-12-31")
    image_urls: Optional[List[str]] = Field(None, description="URLs das imagens do produto", example=["https://exemplo.com/nova-imagem.jpg"])

    class Config:
        schema_extra = {
            "example": {
                "description": "Vestido Floral Verão - Promoção",
                "price": 79.90,
                "stock": 20
            }
        }


class ProductResponse(ProductBase):
    id: int = Field(..., description="ID único do produto", example=1)
    created_at: datetime = Field(..., description="Data de criação", example="2024-01-15T10:30:00")
    updated_at: datetime = Field(..., description="Data da última atualização", example="2024-01-20T14:45:00")

    class Config:
        orm_mode = True
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "description": "Vestido Floral Verão",
                "price": 89.90,
                "barcode": "7891234567890",
                "section": "Roupas Femininas",
                "stock": 15,
                "expiry_date": "2024-12-31",
                "image_urls": ["https://exemplo.com/imagem1.jpg"],
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-20T14:45:00"
            }
        }


class ProductList(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    size: int
