from sqlalchemy import Column, String
from src.models.base import BaseModel
from sqlalchemy.orm import relationship


class Client(BaseModel):
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    orders = relationship("Order", back_populates="client")
