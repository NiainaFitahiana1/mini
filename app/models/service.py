from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    icon = Column(String, nullable=False, default="Code")
    title = Column(String, nullable=False, index=True)
    desc = Column(Text, nullable=False)

    # Optionnel : lien vers un utilisateur (si les services appartiennent à un user)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # user = relationship("User", back_populates="services")

    def __repr__(self):
        return f"<Service(title='{self.title}', icon='{self.icon}')>"
