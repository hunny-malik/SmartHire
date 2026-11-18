import uuid
from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    min_experience_months = Column(Integer, default=12)
    embedding = Column(JSON, nullable=True) # Role profile vector

    # Relationships
    role_skills = relationship("RoleSkill", back_populates="role", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="role", cascade="all, delete-orphan")

class RoleSkill(Base):
    __tablename__ = "role_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id"), nullable=False)
    importance_weight = Column(Integer, default=5) # 1 to 10
    required_level = Column(String(50), default="intermediate") # beginner, intermediate, advanced

    # Relationships
    role = relationship("Role", back_populates="role_skills")
    skill = relationship("Skill", back_populates="role_skills")
