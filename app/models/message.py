from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    sender_identifier = Column(String(255))
    sender_name = Column(String(100))
    content = Column(Text, nullable=False)

    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)

    ip_address = Column(String(45))
    device_info = Column(String(255))
    location_lat = Column(Float)
    location_lon = Column(Float)

    message_type = Column(String(50), default="text", nullable=False)
    attachment_url = Column(String(255))

    parent_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    is_edited = Column(Boolean, default=False, nullable=False)
    edited_at = Column(DateTime)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime)

    extra_data = Column(Text)

    # Relations
    chat = relationship("Chats", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
    parent_message = relationship("Messages", remote_side=[id], back_populates="replies")
    replies = relationship("Messages", back_populates="parent_message", cascade="all, delete-orphan")
