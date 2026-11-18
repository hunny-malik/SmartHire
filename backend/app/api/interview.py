import os
import uuid
import time
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.role import Role
from app.models.candidate_profile import CandidateProfile
from app.models.interview import Interview, InterviewQuestion, InterviewAnswer, InterviewReport
from app.schemas.interview import (
    InterviewStartRequest, QuestionOut, AnswerSubmitRequest, 
    AnswerEvaluationOut, InterviewOut
)
from app.services.auth.security import get_current_user
from app.services.ai.question_generator import question_generator
from app.services.ai.interview_evaluator import interview_evaluator
from app.services.ai.speech_to_text import stt_service
from app.services.ai.text_to_speech import tts_service
from app.services.ai.report_generator import report_generator
from app.core.config import settings
from app.core.logging import logger
from app.core.datetime_utils import utc_now

router = APIRouter(prefix="/interview", tags=["AI Mock Interview"])

@router.post("/start")
async def start_interview(
    request: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    
    # Target role resolution
    role = None
    if request.role_id:
        role = db.query(Role).filter(Role.id == request.role_id).first()
    if not role and current_user.target_role:
        role = db.query(Role).filter(Role.title == current_user.target_role).first()
    if not role:
        role = db.query(Role).first()

    target_role_title = role.title if role else "Software Engineer"
    language = request.language or current_user.language_preference or "English"

    # Create new Interview session
    interview = Interview(
        user_id=current_user.id,
        role_id=role.id if role else None,
        interview_type=request.interview_type or "comprehensive",
        language=language,
        status="active"
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    # Candidate profile details
    cand_name = profile.full_name if profile and profile.full_name else current_user.full_name
    cand_skills = profile.skills if profile and profile.skills else ["Python", "Algorithms"]
    projects = profile.projects if profile and profile.projects else []
    
    # Generate Question 1 dynamically
    q_data = await question_generator.generate_question(
        candidate_name=cand_name,
        target_role=target_role_title,
        skills=cand_skills,
        skill_gaps=["System Design", "Distributed Systems"],
        projects=projects,
        previous_qa=[],
        language=language,
        sequence=1
    )

    # Audio synthesis for question
    tts_res = await tts_service.synthesize(q_data["question"], language=language)

    # Persist Question 1
    question = InterviewQuestion(
        interview_id=interview.id,
        sequence_order=1,
        category=q_data["category"],
        difficulty=q_data["difficulty"],
        skill=q_data["skill"],
        question_text=q_data["question"],
        expected_concepts=q_data["expected_concepts"]
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    return {
        "interview_id": interview.id,
        "role_title": target_role_title,
        "language": language,
        "question": {
            "id": question.id,
            "sequence_order": 1,
            "category": question.category,
            "difficulty": question.difficulty,
            "skill": question.skill,
            "question_text": question.question_text,
            "expected_concepts": question.expected_concepts,
            "audio_base64": tts_res.get("audio_base64")
        }
    }

@router.post("/{interview_id}/answer", response_model=AnswerEvaluationOut)
async def submit_answer(
    interview_id: str,
    payload: AnswerSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(
        Interview.id == interview_id,
        Interview.user_id == current_user.id
    ).first()
    if not interview or interview.status != "active":
        raise HTTPException(status_code=400, detail="Active interview session not found.")

    # Find the current unanswered question
    current_q = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_id == interview.id
    ).order_by(InterviewQuestion.sequence_order.desc()).first()

    if not current_q:
        raise HTTPException(status_code=400, detail="No active question to answer.")

    # Evaluate Candidate Answer
    target_role_title = interview.user.target_role or "Software Engineer"
    eval_res = await interview_evaluator.evaluate_answer(
        question_text=current_q.question_text,
        expected_concepts=current_q.expected_concepts or [],
        candidate_answer=payload.candidate_answer,
        target_role=target_role_title,
        target_skill=current_q.skill,
        language=interview.language
    )

    # Persist Candidate Answer Record
    answer_record = InterviewAnswer(
        question_id=current_q.id,
        candidate_answer=payload.candidate_answer,
        detected_language=eval_res.get("detected_language", "English"),
        technical_accuracy=eval_res["technical_accuracy"],
        communication_score=eval_res["communication_score"],
        confidence_score=eval_res["confidence_score"],
        problem_solving_score=eval_res["problem_solving_score"],
        completeness_score=eval_res["completeness_score"],
        feedback=eval_res["feedback"],
        strengths=eval_res["strengths"],
        weaknesses=eval_res["weaknesses"],
        latency_seconds=payload.latency_seconds or 1.2
    )
    db.add(answer_record)
    db.commit()

    # Determine if next question should be generated (up to 4 questions per interview)
    next_order = current_q.sequence_order + 1
    next_q_out = None
    is_follow_up = (next_order <= 4)

    if is_follow_up:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
        cand_name = profile.full_name if profile and profile.full_name else current_user.full_name
        cand_skills = profile.skills if profile and profile.skills else ["Python", "FastAPI"]
        projects = profile.projects if profile and profile.projects else []

        # Build QA history for context
        all_qa = []
        for q in interview.questions:
            if q.answer:
                all_qa.append({
                    "question_text": q.question_text,
                    "candidate_answer": q.answer.candidate_answer,
                    "technical_accuracy": q.answer.technical_accuracy
                })

        next_q_data = await question_generator.generate_question(
            candidate_name=cand_name,
            target_role=target_role_title,
            skills=cand_skills,
            skill_gaps=["System Design", "Distributed Systems", "Database Optimization"],
            projects=projects,
            previous_qa=all_qa,
            language=interview.language,
            sequence=next_order
        )

        tts_res = await tts_service.synthesize(next_q_data["question"], language=interview.language)

        next_q_model = InterviewQuestion(
            interview_id=interview.id,
            sequence_order=next_order,
            category=next_q_data["category"],
            difficulty=next_q_data["difficulty"],
            skill=next_q_data["skill"],
            question_text=next_q_data["question"],
            expected_concepts=next_q_data["expected_concepts"]
        )
        db.add(next_q_model)
        db.commit()
        db.refresh(next_q_model)

        next_q_out = QuestionOut(
            id=next_q_model.id,
            sequence_order=next_q_model.sequence_order,
            category=next_q_model.category,
            difficulty=next_q_model.difficulty,
            skill=next_q_model.skill,
            question_text=next_q_model.question_text,
            expected_concepts=next_q_model.expected_concepts,
            audio_base64=tts_res.get("audio_base64")
        )
    else:
        # Finalize interview
        await _finalize_interview(interview, db)

    return AnswerEvaluationOut(
        technical_accuracy=eval_res["technical_accuracy"],
        communication_score=eval_res["communication_score"],
        confidence_score=eval_res["confidence_score"],
        problem_solving_score=eval_res["problem_solving_score"],
        completeness_score=eval_res["completeness_score"],
        feedback=eval_res["feedback"],
        strengths=eval_res["strengths"],
        weaknesses=eval_res["weaknesses"],
        is_follow_up=is_follow_up,
        next_question=next_q_out
    )

@router.post("/{interview_id}/voice")
async def submit_voice_answer(
    interview_id: str,
    audio: UploadFile = File(...),
    live_transcript: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    audio_bytes = await audio.read()
    stt_res = await stt_service.transcribe_audio(
        audio_bytes=audio_bytes, 
        filename=audio.filename or "recording.webm",
        fallback_transcript=live_transcript
    )
    transcript = stt_res.get("transcript", "").strip()
    if not transcript and live_transcript:
        transcript = live_transcript.strip()

    latency = round(time.time() - start_time, 2)

    # Submit transcribed text into evaluation flow
    ans_submit = AnswerSubmitRequest(candidate_answer=transcript, latency_seconds=latency)
    eval_result = await submit_answer(interview_id, ans_submit, current_user, db)

    return {
        "transcript": transcript,
        "stt_latency_seconds": stt_res.get("latency_seconds", 0.5),
        "total_latency_seconds": latency,
        "evaluation": eval_result
    }

@router.post("/{interview_id}/complete")
async def complete_interview(
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

    await _finalize_interview(interview, db)
    return {"status": "completed", "interview_id": interview.id, "overall_score": interview.overall_score}

async def _finalize_interview(interview: Interview, db: Session):
    interview.status = "completed"
    interview.ended_at = utc_now()

    # Aggregate scores from all answered questions
    answers = [q.answer for q in interview.questions if q.answer]
    if answers:
        tech_avg = sum(a.technical_accuracy for a in answers) / len(answers)
        comm_avg = sum(a.communication_score for a in answers) / len(answers)
        ps_avg = sum(a.problem_solving_score for a in answers) / len(answers)
        conf_avg = sum(a.confidence_score for a in answers) / len(answers)
        overall = round((tech_avg * 0.4 + comm_avg * 0.2 + ps_avg * 0.25 + conf_avg * 0.15), 1)
    else:
        tech_avg, comm_avg, ps_avg, conf_avg, overall = 75.0, 75.0, 75.0, 75.0, 75.0

    interview.overall_score = overall

    # Gather collective strengths & weaknesses
    all_strengths = []
    all_weaknesses = []
    qa_records = []
    for q in interview.questions:
        if q.answer:
            all_strengths.extend(q.answer.strengths or [])
            all_weaknesses.extend(q.answer.weaknesses or [])
            qa_records.append({
                "sequence_order": q.sequence_order,
                "category": q.category,
                "skill": q.skill,
                "question_text": q.question_text,
                "candidate_answer": q.answer.candidate_answer,
                "technical_accuracy": q.answer.technical_accuracy,
                "communication_score": q.answer.communication_score,
                "problem_solving_score": q.answer.problem_solving_score,
                "confidence_score": q.answer.confidence_score,
                "feedback": q.answer.feedback,
                "strengths": q.answer.strengths or [],
                "weaknesses": q.answer.weaknesses or []
            })

    unique_strengths = list(dict.fromkeys(all_strengths))[:4] or ["Solid technical foundations", "Clear conversational communication"]
    unique_weaknesses = list(dict.fromkeys(all_weaknesses))[:3] or ["Provide deeper architectural metrics", "Elaborate on edge-case scaling"]

    summary = (
        f"Candidate scored an overall {overall}%. Demonstrated {round(tech_avg, 1)}% in Technical Accuracy "
        f"and {round(comm_avg, 1)}% in Communication. Solid performance with key opportunities in advanced system design."
    )

    # Generate PDF report file
    reports_dir = os.path.join(settings.UPLOAD_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    pdf_filename = f"report_{interview.id}.pdf"
    pdf_path = os.path.join(reports_dir, pdf_filename)

    report_payload = {
        "candidate_name": interview.user.full_name,
        "target_role": interview.user.target_role or "Software Engineer",
        "interview_date": interview.started_at.strftime("%B %d, %Y"),
        "overall_score": overall,
        "technical_score": round(tech_avg, 1),
        "communication_score": round(comm_avg, 1),
        "problem_solving_score": round(ps_avg, 1),
        "confidence_score": round(conf_avg, 1),
        "summary": summary,
        "strengths": unique_strengths,
        "weaknesses": unique_weaknesses,
        "revision_topics": ["Distributed Caching & Redis", "System Design & Scaling", "Database Index Optimization"],
        "qa_records": qa_records
    }

    try:
        report_generator.generate_pdf_report(report_payload, pdf_path)
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}")

    # Create or update InterviewReport record
    rep_obj = db.query(InterviewReport).filter(InterviewReport.interview_id == interview.id).first()
    if not rep_obj:
        rep_obj = InterviewReport(
            interview_id=interview.id,
            overall_score=overall,
            technical_score=round(tech_avg, 1),
            communication_score=round(comm_avg, 1),
            problem_solving_score=round(ps_avg, 1),
            confidence_score=round(conf_avg, 1),
            summary=summary,
            strengths=unique_strengths,
            weaknesses=unique_weaknesses,
            improvement_suggestions=[
                "Practice high-level distributed systems trade-offs.",
                "Structure technical answers using the Situation-Task-Action-Result (STAR) technique."
            ],
            revision_topics=["System Design", "Database Optimization", "Low-Level Design"],
            pdf_report_path=pdf_path
        )
        db.add(rep_obj)
    db.commit()

@router.get("/history", response_model=List[InterviewOut])
def get_interview_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    interviews = db.query(Interview).filter(
        Interview.user_id == current_user.id
    ).order_by(Interview.started_at.desc()).all()

    out = []
    for inv in interviews:
        out.append({
            "id": inv.id,
            "role_id": inv.role_id,
            "role_title": inv.user.target_role or "Software Engineer",
            "interview_type": inv.interview_type,
            "language": inv.language,
            "status": inv.status,
            "overall_score": inv.overall_score,
            "started_at": inv.started_at,
            "questions_count": len(inv.questions)
        })
    return out
