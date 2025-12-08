from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class ProductKey(Base, TimestampMixin):
    __tablename__ = "product_keys"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    key_value = Column(String(500), nullable=False)
    duration = Column(String(100), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    
    product = relationship("Product", back_populates="keys")
    
    def __repr__(self):
        return f"<ProductKey(id={self.id}, product_id={self.product_id}, is_used={self.is_used})>"
