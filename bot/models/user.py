from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base, TimestampMixin


class UserStatus(enum.Enum):
    FREE = "free"
    PREMIUM = "premium"


class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    balance = Column(Float, default=0.0, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.FREE, nullable=False)
    is_reseller = Column(Boolean, default=False, nullable=False)
    last_purchase_at = Column(DateTime, nullable=True)
    
    orders = relationship("Order", back_populates="user", lazy="selectin")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, status={self.status})>"
