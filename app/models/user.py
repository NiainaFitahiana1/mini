from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
from ..db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, default=1)

    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    bio = Column(String(1000), nullable=True)
    specialite = Column(String(150), nullable=True)

    lien_avatar = Column(String(255))  
    lien_github = Column(String(255))
    lien_linkedin = Column(String(255))
    lien_dribbble = Column(String(255))
    lien_portaljob = Column(String(255))

    telephone = Column(String(50))
    email = Column(String(150), unique=True, nullable=False, index=True)

    adresse = Column(String(255))
    disponibilite = Column(Boolean, nullable=False, default=True)
    date_de_naissance = Column(Date, nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    # Relations
    sent_messages = relationship(
        "Messages",
        back_populates="sender",
        foreign_keys="Messages.sender_id",
        cascade="all, delete-orphan"
    )
    parcours = relationship(
        "Parcours",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    chats = relationship(
        "Chats",
        back_populates="user",
        cascade="all, delete-orphan"
    )
