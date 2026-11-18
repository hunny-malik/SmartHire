from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class JobOut(BaseModel):
    id: Optional[str] = None
    external_id: Optional[str] = None
    title: str
    company: str
    location: str
    job_type: str
    salary_range: Optional[str] = None
    experience_level: str
    required_skills: List[str] = []
    description: str
    apply_url: str
    source: str
    posted_date: str

    model_config = ConfigDict(from_attributes=True)

class JobMatchOut(BaseModel):
    job: JobOut
    bm25_score: float
    cosine_score: float
    final_score: float
    matched_skills: List[str]
    is_live_external: bool = False

class JobSearchQuery(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    remote_only: Optional[bool] = False
    min_match_score: Optional[float] = 0.0
