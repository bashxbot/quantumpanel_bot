from sqlalchemy import Column, Integer, String
from .base import Base, TimestampMixin


class TrustedSeller(Base, TimestampMixin):
    __tablename__ = "trusted_sellers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    description = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<TrustedSeller(id={self.id}, username={self.username})>"
