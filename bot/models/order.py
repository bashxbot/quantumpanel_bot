from sqlalchemy import Column, Integer, BigInteger, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base, TimestampMixin


class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    duration = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    key_value = Column(String(500), nullable=True)
    purchased_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="orders")
    product = relationship("Product", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, product_name={self.product_name})>"
