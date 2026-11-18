from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.candidate_profile import CandidateProfile
from app.schemas.job import JobMatchOut, JobSearchQuery
from app.services.auth.security import get_current_user
from app.services.jobs.service import job_service

router = APIRouter(prefix="/jobs", tags=["Job Matching"])

@router.get("/recommendations", response_model=List[JobMatchOut])
async def get_job_recommendations(
    role: Optional[str] = Query(None, description="Target role override"),
    location: Optional[str] = Query(None, description="Target location"),
    limit: int = Query(10, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a resume first to receive personalized job matches."
        )

    target_role = role or current_user.target_role or (profile.job_titles[0] if profile.job_titles else "Software Engineer")
    matches = await job_service.get_recommended_jobs(
        profile=profile,
        target_role=target_role,
        location=location,
        limit=limit
    )
    return matches

@router.post("/search", response_model=List[JobMatchOut])
async def search_jobs(
    query_body: JobSearchQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id, skills=[], job_titles=[query_body.query or "Software Engineer"])

    matches = await job_service.get_recommended_jobs(
        profile=profile,
        target_role=query_body.query,
        location=query_body.location,
        limit=10
    )

    if query_body.min_match_score and query_body.min_match_score > 0:
        matches = [m for m in matches if m["final_score"] >= query_body.min_match_score]

    return matches
