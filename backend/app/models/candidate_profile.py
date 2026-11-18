import uuid
from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.core.datetime_utils import utc_now

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    resume_id = Column(String(36), ForeignKey("resumes.id"), nullable=True)
    
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Structured resume sections stored as JSON
    education = Column(JSON, default=list) # [{degree, institution, year, score}]
    skills = Column(JSON, default=list) # ["Python", "FastAPI", "Docker"]
    experience = Column(JSON, default=list) # [{title, company, duration, responsibilities}]
    projects = Column(JSON, default=list) # [{title, description, technologies}]
    certifications = Column(JSON, default=list) # [{title, issuer, year}]
    job_titles = Column(JSON, default=list) # ["Backend Developer", "Software Engineer"]
    
    # Semantic embedding vector (stored as JSON array of floats)
    embedding = Column(JSON, nullable=True)
    
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User", back_populates="profile")
    resume = relationship("Resume", back_populates="profile")
