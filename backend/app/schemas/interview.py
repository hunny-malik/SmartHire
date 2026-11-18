from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class InterviewStartRequest(BaseModel):
    role_id: Optional[str] = None
    language: Optional[str] = "English" # English, Hindi, Hinglish
    interview_type: Optional[str] = "comprehensive" # technical, behavioral, comprehensive

class QuestionOut(BaseModel):
    id: str
    sequence_order: int
    category: str
    difficulty: str
    skill: Optional[str] = None
    question_text: str
    expected_concepts: List[str] = []
    audio_base64: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AnswerSubmitRequest(BaseModel):
    candidate_answer: str
    latency_seconds: Optional[float] = 1.2

class AnswerEvaluationOut(BaseModel):
    technical_accuracy: float
    communication_score: float
    confidence_score: float
    problem_solving_score: float
    completeness_score: float
    feedback: str
    strengths: List[str]
    weaknesses: List[str]
    is_follow_up: bool
    next_question: Optional[QuestionOut] = None

class InterviewOut(BaseModel):
    id: str
    role_id: Optional[str] = None
    role_title: Optional[str] = None
    interview_type: str
    language: str
    status: str
    overall_score: Optional[float] = None
    started_at: datetime
    questions_count: int = 0

    model_config = ConfigDict(from_attributes=True)
