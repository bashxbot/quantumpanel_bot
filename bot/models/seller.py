from sqlalchemy import Column, Integer, String, Text, Boolean
from .base import Base, TimestampMixin


class TrustedSeller(Base, TimestampMixin):
    __tablename__ = "trusted_sellers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    platforms = Column(Text, nullable=True)  # JSON string or formatted text
    country = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<TrustedSeller(id={self.id}, username={self.username})>"
