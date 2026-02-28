from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class PushToken(Base):
    __tablename__ = "push_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())