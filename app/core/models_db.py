from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    email = Column(String, unique = True, nullable = False)
    hashed_password = Column(String, nullable = False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key = True, index=True)
    user_id = Column(Integer,ForeignKey("users.id"), nullable = False)
    role = Column(String, nullable = False)
    content = Column(Text, nullable = False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
