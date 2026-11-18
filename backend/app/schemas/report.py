from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class QuestionAnswerRecord(BaseModel):
    sequence_order: int
    category: str
    skill: Optional[str] = None
    question_text: str
    candidate_answer: str
    technical_accuracy: float
    communication_score: float
    problem_solving_score: float
    confidence_score: float
    feedback: str
    strengths: List[str]
    weaknesses: List[str]

class InterviewReportOut(BaseModel):
    id: str
    interview_id: str
    candidate_name: str
    target_role: str
    interview_date: str
    overall_score: float
    technical_score: float
    communication_score: float
    problem_solving_score: float
    confidence_score: float
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    revision_topics: List[str]
    qa_records: List[QuestionAnswerRecord] = []
    pdf_download_url: Optional[str] = None
