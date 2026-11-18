import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.interview import Interview, InterviewReport
from app.schemas.report import InterviewReportOut, QuestionAnswerRecord
from app.services.auth.security import get_current_user

router = APIRouter(prefix="/reports", tags=["Interview Reports"])

@router.get("/{interview_id}", response_model=InterviewReportOut)
def get_interview_report(
    interview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    report = db.query(InterviewReport).filter(InterviewReport.interview_id == interview.id).first()
    if not report:
        raise HTTPException(
            status_code=400,
            detail="Report not yet generated for this interview. Please complete the interview first."
        )

    # Compile QA records
    qa_list = []
    for q in interview.questions:
        if q.answer:
            qa_list.append(QuestionAnswerRecord(
                sequence_order=q.sequence_order,
                category=q.category,
                skill=q.skill,
                question_text=q.question_text,
                candidate_answer=q.answer.candidate_answer,
                technical_accuracy=q.answer.technical_accuracy,
                communication_score=q.answer.communication_score,
                problem_solving_score=q.answer.problem_solving_score,
                confidence_score=q.answer.confidence_score,
                feedback=q.answer.feedback or "",
                strengths=q.answer.strengths or [],
                weaknesses=q.answer.weaknesses or []
            ))

    pdf_url = f"/api/reports/{interview_id}/download" if report.pdf_report_path else None

    return InterviewReportOut(
        id=report.id,
        interview_id=interview.id,
        candidate_name=interview.user.full_name,
        target_role=interview.user.target_role or "Software Engineer",
        interview_date=report.created_at.strftime("%B %d, %Y"),
        overall_score=report.overall_score,
        technical_score=report.technical_score,
        communication_score=report.communication_score,
        problem_solving_score=report.problem_solving_score,
        confidence_score=report.confidence_score,
        summary=report.summary,
        strengths=report.strengths or [],
        weaknesses=report.weaknesses or [],
        improvement_suggestions=report.improvement_suggestions or [],
        revision_topics=report.revision_topics or [],
        qa_records=qa_list,
        pdf_download_url=pdf_url
    )

@router.get("/{interview_id}/download")
def download_interview_report_pdf(
    interview_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")

    report = db.query(InterviewReport).filter(InterviewReport.interview_id == interview.id).first()
    if not report or not report.pdf_report_path or not os.path.exists(report.pdf_report_path):
        raise HTTPException(status_code=404, detail="PDF report file not found on server.")

    return FileResponse(
        path=report.pdf_report_path,
        filename=f"SmartHire_Report_{current_user.full_name.replace(' ', '_')}_{interview.id[:8]}.pdf",
        media_type="application/pdf"
    )
