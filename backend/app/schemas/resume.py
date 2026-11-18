from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

class ResumeOut(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: str
    file_size: int
    parsing_status: str
    uploaded_at: datetime
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CandidateProfileOut(BaseModel):
    id: str
    user_id: str
    resume_id: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: List[Dict[str, Any]] = []
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[Dict[str, Any]] = []
    job_titles: List[str] = []
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CandidateProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    job_titles: Optional[List[str]] = None
