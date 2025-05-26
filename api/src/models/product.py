from sqlalchemy import Column, String, Float, Integer, Date, Text
from src.models.base import BaseModel

class Product(BaseModel):
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    barcode = Column(String, unique=True, index=True, nullable=True)
    section = Column(String, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    expiry_date = Column(Date, nullable=True)
    image_urls = Column(Text, nullable=True)
