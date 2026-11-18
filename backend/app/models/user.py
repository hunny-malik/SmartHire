import uuid
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.core.datetime_utils import utc_now

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    target_role = Column(String(255), nullable=True)
    language_preference = Column(String(50), default="English") # English, Hindi, Hinglish
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("CandidateProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    roadmaps = relationship("LearningRoadmap", back_populates="user", cascade="all, delete-orphan")
