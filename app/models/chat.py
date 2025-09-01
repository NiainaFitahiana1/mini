from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

class Chats(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    participant_identifier = Column(String(255), nullable=False)
    participant_name = Column(String(100))
    participant_email = Column(String(150))
    participant_phone = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_message_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    chat_type = Column(String(50), default="private", nullable=False)
    chat_name = Column(String(100))
    last_ip_address = Column(String(45))
    extra_data = Column(Text)

    # Relations
    user = relationship("User", back_populates="chats")
    messages = relationship("Messages", back_populates="chat", cascade="all, delete-orphan")
