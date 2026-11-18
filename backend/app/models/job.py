import uuid
from sqlalchemy import Column, String, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.core.datetime_utils import utc_now

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id = Column(String(255), unique=True, index=True, nullable=True)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    job_type = Column(String(100), default="Full-time") # Full-time, Remote, Contract, Hybrid
    salary_range = Column(String(100), nullable=True)
    experience_level = Column(String(100), default="Mid-Senior level")
    required_skills = Column(JSON, default=list)
    description = Column(Text, nullable=False)
    apply_url = Column(String(1024), nullable=False)
    source = Column(String(100), default="Live Aggregate") # Google Jobs, LinkedIn, TechDirect
    posted_date = Column(String(100), default="Recent")
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")

class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    bm25_score = Column(Float, default=0.0)
    cosine_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0) # Combined hybrid score
    matched_skills = Column(JSON, default=list)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    job = relationship("Job", back_populates="matches")
