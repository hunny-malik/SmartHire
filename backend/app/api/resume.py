import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.candidate_profile import CandidateProfile
from app.schemas.resume import ResumeOut, CandidateProfileOut, CandidateProfileUpdate
from app.services.auth.security import get_current_user
from app.services.ai.resume_parser import resume_parser
from app.core.config import settings
from app.core.logging import logger

router = APIRouter(prefix="/resume", tags=["Resume Operations"])

@router.post("/upload", response_model=CandidateProfileOut)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Validation
    filename = file.filename or "resume.pdf"
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Please upload PDF or DOCX (allowed: {', '.join(settings.ALLOWED_EXTENSIONS)})."
        )

    # Read content & validate size
    contents = await file.read()
    file_size = len(contents)
    if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )

    # Save to disk
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    saved_filename = f"{uuid.uuid4()}_{filename}"
    saved_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
    with open(saved_path, "wb") as f:
        f.write(contents)

    # Create Resume DB Record
    resume_obj = Resume(
        user_id=current_user.id,
        filename=filename,
        file_path=saved_path,
        file_type=file_ext.strip("."),
        file_size=file_size,
        parsing_status="processing"
    )
    db.add(resume_obj)
    db.commit()
    db.refresh(resume_obj)

    # 2. Extract Text & Parse
    try:
        raw_text = resume_parser.extract_text(saved_path, file_ext)
        resume_obj.raw_text = raw_text

        parsed_data = resume_parser.parse_resume_text(raw_text)
        resume_obj.parsing_status = "completed"

        # 3. Create or Update CandidateProfile
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
        if not profile:
            profile = CandidateProfile(
                user_id=current_user.id,
                resume_id=resume_obj.id,
                full_name=parsed_data.get("name") or current_user.full_name,
                email=parsed_data.get("email") or current_user.email,
                phone=parsed_data.get("phone"),
                education=parsed_data.get("education", []),
                skills=parsed_data.get("skills", []),
                experience=parsed_data.get("experience", []),
                projects=parsed_data.get("projects", []),
                certifications=parsed_data.get("certifications", []),
                job_titles=parsed_data.get("job_titles", []),
                embedding=parsed_data.get("embedding")
            )
            db.add(profile)
        else:
            profile.resume_id = resume_obj.id
            profile.full_name = parsed_data.get("name") or profile.full_name
            profile.email = parsed_data.get("email") or profile.email
            profile.phone = parsed_data.get("phone") or profile.phone
            profile.education = parsed_data.get("education", [])
            profile.skills = parsed_data.get("skills", [])
            profile.experience = parsed_data.get("experience", [])
            profile.projects = parsed_data.get("projects", [])
            profile.certifications = parsed_data.get("certifications", [])
            profile.job_titles = parsed_data.get("job_titles", [])
            profile.embedding = parsed_data.get("embedding")

        # Auto-update user's target role if not set
        if not current_user.target_role and profile.job_titles:
            current_user.target_role = profile.job_titles[0]

        db.commit()
        db.refresh(profile)
        return profile

    except Exception as e:
        logger.error(f"Error parsing resume {filename}: {e}")
        resume_obj.parsing_status = "failed"
        resume_obj.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume document: {str(e)}"
        )

@router.get("/profile", response_model=CandidateProfileOut)
def get_candidate_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No candidate profile found. Please upload a resume first."
        )
    return profile

@router.put("/profile", response_model=CandidateProfileOut)
def update_candidate_profile(
    update_data: CandidateProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No candidate profile found."
        )

    if update_data.full_name is not None:
        profile.full_name = update_data.full_name
    if update_data.email is not None:
        profile.email = update_data.email
    if update_data.phone is not None:
        profile.phone = update_data.phone
    if update_data.skills is not None:
        profile.skills = update_data.skills
    if update_data.job_titles is not None:
        profile.job_titles = update_data.job_titles

    db.commit()
    db.refresh(profile)
    return profile

@router.get("/download/{resume_id}")
def download_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume or not os.path.exists(resume.file_path):
        raise HTTPException(status_code=404, detail="Resume file not found.")
    return FileResponse(path=resume.file_path, filename=resume.filename, media_type="application/octet-stream")
