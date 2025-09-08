from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    icon = Column(String, nullable=False, default="Code")  # Icône associée à la compétence
    name = Column(String, nullable=False, index=True)      # Nom de la compétence
    level = Column(String, nullable=False, default="Beginner")  # Niveau (Beginner, Intermediate, Advanced, Expert)
    desc = Column(Text, nullable=True)                     # Description optionnelle

    # Lien vers un utilisateur (chaque skill appartient à un user)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # user = relationship("User", back_populates="skills")

    def __repr__(self):
        return f"<Skill(name='{self.name}', level='{self.level}', icon='{self.icon}')>"
