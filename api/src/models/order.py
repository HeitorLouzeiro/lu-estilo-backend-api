import enum

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from src.config.database import Base
from src.models.base import BaseModel


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


class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    # Relacionamentos
    order = relationship("Order", back_populates="items")
    product = relationship("Product")


class Order(BaseModel):
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    status = Column(Enum(OrderStatus),
                    default=OrderStatus.PENDING, nullable=False)
    total_amount = Column(Float, nullable=False)

    # Relacionamentos
    client = relationship("Client", back_populates="orders")
    products = relationship("Product", secondary=order_products)
    items = relationship("OrderItem", back_populates="order", lazy="joined")
