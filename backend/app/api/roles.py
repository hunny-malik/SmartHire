from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.role import Role, RoleSkill
from app.models.candidate_profile import CandidateProfile
from app.schemas.role import RoleOut, RoleRecommendationOut
from app.services.auth.security import get_current_user
from app.services.ai.role_matcher import role_matcher

router = APIRouter(prefix="/roles", tags=["Role Recommendations"])

@router.get("/recommendations", response_model=List[RoleRecommendationOut])
def get_role_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a resume first to receive personalized role recommendations."
        )

    recommendations = role_matcher.match_candidate_to_roles(profile, db)
    return recommendations

@router.get("", response_model=List[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    out = []
    for r in roles:
        req_skills = []
        for rs in r.role_skills:
            if rs.skill:
                req_skills.append({
                    "skill_name": rs.skill.name,
                    "category": rs.skill.category,
                    "importance_weight": rs.importance_weight,
                    "required_level": rs.required_level
                })
        out.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "category": r.category,
            "min_experience_months": r.min_experience_months,
            "required_skills": req_skills
        })
    return out

@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: str, db: Session = Depends(get_db)):
    r = db.query(Role).filter(Role.id == role_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Role not found.")
    req_skills = [
        {
            "skill_name": rs.skill.name,
            "category": rs.skill.category,
            "importance_weight": rs.importance_weight,
            "required_level": rs.required_level
        }
        for rs in r.role_skills if rs.skill
    ]
    return {
        "id": r.id,
        "title": r.title,
        "description": r.description,
        "category": r.category,
        "min_experience_months": r.min_experience_months,
        "required_skills": req_skills
    }
