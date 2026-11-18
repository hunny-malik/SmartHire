import uuid
from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False) # Programming, Cloud, Data, Frontend, Backend, etc.
    esco_uri = Column(String(255), nullable=True) # ESCO / O*NET taxonomy reference
    prerequisites = Column(JSON, default=list) # List of prerequisite skill names
    difficulty_level = Column(String(50), default="intermediate") # beginner, intermediate, advanced

    # Relationships
    role_skills = relationship("RoleSkill", back_populates="skill", cascade="all, delete-orphan")
