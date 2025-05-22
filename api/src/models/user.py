from sqlalchemy import Column, String, Boolean, Enum
import enum
from src.models.base import BaseModel

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(BaseModel):
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
