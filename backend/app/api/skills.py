from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.role import Role
from app.models.skill import Skill
from app.models.candidate_profile import CandidateProfile
from app.models.skill_gap import SkillGap, LearningRoadmap
from app.schemas.skill import (
    SkillGapRequest, SkillGapOut, RoadmapItemOut, RoadmapUpdate, SkillOut
)
from app.services.auth.security import get_current_user
from app.services.ai.skill_gap_engine import skill_gap_engine

router = APIRouter(prefix="/skills", tags=["Skill Gap & Learning Roadmap"])

@router.post("/analyze", response_model=SkillGapOut)
def analyze_skill_gap(
    request: SkillGapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a resume first to run skill gap analysis."
        )

    role = db.query(Role).filter(Role.id == request.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target role not found.")

    # Run ontology-based gap analysis
    gap_result = skill_gap_engine.analyze_skill_gap(profile, role, db)

    # Persist SkillGap Record
    existing_gap = db.query(SkillGap).filter(
        SkillGap.user_id == current_user.id,
        SkillGap.role_id == role.id
    ).first()

    if not existing_gap:
        existing_gap = SkillGap(
            user_id=current_user.id,
            role_id=role.id,
            match_percentage=gap_result["match_percentage"],
            matching_skills=gap_result["matching_skills"],
            missing_skills=gap_result["missing_skills"],
            learning_priority_dag=gap_result["prerequisite_dag"]
        )
        db.add(existing_gap)
    else:
        existing_gap.match_percentage = gap_result["match_percentage"]
        existing_gap.matching_skills = gap_result["matching_skills"]
        existing_gap.missing_skills = gap_result["missing_skills"]
        existing_gap.learning_priority_dag = gap_result["prerequisite_dag"]

    # Also set target_role on user
    current_user.target_role = role.title

    # Generate and persist personalized roadmap
    skill_gap_engine.generate_roadmap_plan(
        user_id=current_user.id,
        role_id=role.id,
        missing_skills=gap_result["missing_skills"],
        db=db
    )

    db.commit()
    return gap_result

@router.get("/roadmap", response_model=List[RoadmapItemOut])
def get_learning_roadmap(
    role_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(LearningRoadmap).filter(LearningRoadmap.user_id == current_user.id)
    if role_id:
        query = query.filter(LearningRoadmap.role_id == role_id)
    
    items = query.order_by(LearningRoadmap.week_number.asc()).all()
    if not items:
        # If user has a target role, generate roadmap automatically
        target_role_title = current_user.target_role or "Software Engineer"
        role = db.query(Role).filter(Role.title == target_role_title).first()
        if role:
            profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
            if profile:
                gap_res = skill_gap_engine.analyze_skill_gap(profile, role, db)
                skill_gap_engine.generate_roadmap_plan(current_user.id, role.id, gap_res["missing_skills"], db)
                items = db.query(LearningRoadmap).filter(
                    LearningRoadmap.user_id == current_user.id,
                    LearningRoadmap.role_id == role.id
                ).order_by(LearningRoadmap.week_number.asc()).all()

    return items

@router.patch("/roadmap/{item_id}", response_model=RoadmapItemOut)
def update_roadmap_item(
    item_id: str,
    payload: RoadmapUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(LearningRoadmap).filter(
        LearningRoadmap.id == item_id,
        LearningRoadmap.user_id == current_user.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Roadmap item not found.")

    if payload.status in ["not_started", "in_progress", "completed"]:
        item.status = payload.status

    db.commit()
    db.refresh(item)
    return item

@router.get("/all", response_model=List[SkillOut])
def get_all_skills(db: Session = Depends(get_db)):
    return db.query(Skill).all()
