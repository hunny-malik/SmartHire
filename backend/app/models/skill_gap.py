import uuid
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.core.datetime_utils import utc_now

class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    match_percentage = Column(Float, default=0.0)
    matching_skills = Column(JSON, default=list) # [{name, level, importance}]
    missing_skills = Column(JSON, default=list) # [{name, required_level, priority, gap_score, prerequisites, learning_resources, estimated_time}]
    learning_priority_dag = Column(JSON, default=list) # topological sort order
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    role = relationship("Role", back_populates="skill_gaps")

class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    phase_title = Column(String(255), nullable=False)
    skill_name = Column(String(100), nullable=False)
    status = Column(String(50), default="not_started") # not_started, in_progress, completed
    learning_resources = Column(JSON, default=list) # [{title, url, type, est_hours}]
    estimated_hours = Column(Integer, default=10)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User", back_populates="roadmaps")
