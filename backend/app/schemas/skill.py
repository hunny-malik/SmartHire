from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional

class SkillOut(BaseModel):
    id: str
    name: str
    category: str
    difficulty_level: str
    prerequisites: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class SkillGapRequest(BaseModel):
    role_id: str

class SkillGapItem(BaseModel):
    name: str
    current_level: str # none, beginner, intermediate, advanced
    required_level: str
    gap_score: float # 0 to 100
    importance: int # 1 to 10
    priority: str # critical, high, medium, low
    prerequisites: List[str] = []
    recommended_resources: List[Dict[str, Any]] = []
    estimated_learning_hours: int = 10

class SkillGapOut(BaseModel):
    role_id: str
    role_title: str
    match_percentage: float
    gap_percentage: float
    matching_skills: List[Dict[str, Any]]
    missing_skills: List[SkillGapItem]
    prerequisite_dag: Dict[str, Any] # Graph nodes & edges: {"nodes": [...], "edges": [...]}
    career_transition_path: List[str]

class RoadmapItemOut(BaseModel):
    id: str
    week_number: int
    phase_title: str
    skill_name: str
    status: str # not_started, in_progress, completed
    learning_resources: List[Dict[str, Any]]
    estimated_hours: int

    model_config = ConfigDict(from_attributes=True)

class RoadmapUpdate(BaseModel):
    status: str # not_started, in_progress, completed
