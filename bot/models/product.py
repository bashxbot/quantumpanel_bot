from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_file_id = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    prices = relationship("ProductPrice", back_populates="product", lazy="selectin", cascade="all, delete-orphan")
    keys = relationship("ProductKey", back_populates="product", lazy="selectin", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="product", lazy="selectin")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name})>"


class ProductPrice(Base, TimestampMixin):
    __tablename__ = "product_prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    duration = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    
    product = relationship("Product", back_populates="prices")
    
    def __repr__(self):
        return f"<ProductPrice(product_id={self.product_id}, duration={self.duration}, price={self.price})>"
