from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class RoleSkillOut(BaseModel):
    skill_name: str
    category: str
    importance_weight: int
    required_level: str

    model_config = ConfigDict(from_attributes=True)

class RoleOut(BaseModel):
    id: str
    title: str
    description: str
    category: str
    min_experience_months: int
    required_skills: List[RoleSkillOut] = []

    model_config = ConfigDict(from_attributes=True)

class RoleRecommendationOut(BaseModel):
    role_id: str
    role_title: str
    category: str
    match_percentage: float
    matching_skills: List[str]
    missing_skills: List[str]
    reason: str
