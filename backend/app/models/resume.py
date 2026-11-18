import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.core.datetime_utils import utc_now

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(50), nullable=False) # pdf, docx
    file_size = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=True)
    parsing_status = Column(String(50), default="pending") # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="resumes")
    profile = relationship("CandidateProfile", back_populates="resume", uselist=False, cascade="all, delete-orphan")
