from sqlalchemy import Column, Integer, String, Text,ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base

class Projets(Base):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    desc = Column(Text, nullable=False)
    type = Column(String, nullable=False, default="Web")
    demo = Column(String, nullable=True)
    repo = Column(String, nullable=True)
    photo = Column(String, nullable=True)

    # Optional: Add relationship if projects are linked to a user or other table
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # user = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<Projet(title='{self.title}', type='{self.type}')>"