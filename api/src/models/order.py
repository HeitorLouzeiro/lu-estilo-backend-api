from sqlalchemy import Column, String, Float, Integer, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
import enum
from src.models.base import BaseModel
from src.config.database import Base

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Tabela de associação para relacionamento muitos-para-muitos
order_products = Table(
    'order_products',
    Base.metadata,
    Column('order_id', Integer, ForeignKey('order.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('product.id'), primary_key=True),
    Column('quantity', Integer, nullable=False),
    Column('unit_price', Float, nullable=False)
)

class Order(BaseModel):
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Relacionamentos
    client = relationship("Client", back_populates="orders")
    products = relationship("Product", secondary=order_products)
