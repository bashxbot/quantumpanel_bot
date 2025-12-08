from sqlalchemy import Column, Integer, BigInteger, String, Boolean
from .base import Base, TimestampMixin


class Admin(Base, TimestampMixin):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    is_root = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<Admin(id={self.id}, telegram_id={self.telegram_id}, is_root={self.is_root})>"
