from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base

class Parcours(Base):
    __tablename__ = "parcours"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    year = Column(String, nullable=False)
    role = Column(String, nullable=False)
    company = Column(String, nullable=False)
    description = Column(String, nullable=False)
    stack = Column(Text)  # JSON

    user = relationship("User", back_populates="parcours")
