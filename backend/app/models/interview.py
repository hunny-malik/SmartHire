import uuid
from sqlalchemy import Column, String, Integer, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.core.datetime_utils import utc_now

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)
    interview_type = Column(String(50), default="comprehensive") # technical, behavioral, comprehensive
    language = Column(String(50), default="English") # English, Hindi, Hinglish
    status = Column(String(50), default="active") # active, completed, cancelled
    overall_score = Column(Float, nullable=True)
    started_at = Column(DateTime, default=utc_now)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="interviews")
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan", order_by="InterviewQuestion.sequence_order")
    report = relationship("InterviewReport", back_populates="interview", uselist=False, cascade="all, delete-orphan")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String(36), ForeignKey("interviews.id"), nullable=False)
    sequence_order = Column(Integer, default=1)
    category = Column(String(50), default="technical") # technical, behavioral, situational, system_design
    difficulty = Column(String(50), default="medium") # easy, medium, hard
    skill = Column(String(100), nullable=True)
    question_text = Column(Text, nullable=False)
    expected_concepts = Column(JSON, default=list)
    audio_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("interview_questions.id"), nullable=False, unique=True)
    candidate_answer = Column(Text, nullable=False)
    detected_language = Column(String(50), default="English")
    audio_recording_url = Column(String(512), nullable=True)
    
    # Detailed grading metrics (0-100)
    technical_accuracy = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    problem_solving_score = Column(Float, default=0.0)
    completeness_score = Column(Float, default=0.0)
    
    feedback = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    latency_seconds = Column(Float, default=0.0)
    answered_at = Column(DateTime, default=utc_now)

    # Relationships
    question = relationship("InterviewQuestion", back_populates="answer")

class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String(36), ForeignKey("interviews.id"), nullable=False, unique=True)
    
    overall_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    problem_solving_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    
    summary = Column(Text, nullable=False)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    improvement_suggestions = Column(JSON, default=list)
    revision_topics = Column(JSON, default=list)
    
    pdf_report_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    interview = relationship("Interview", back_populates="report")
