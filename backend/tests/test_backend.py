import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base, get_db
from app.database.seed_data import seed_database
from main import app
from app.services.ai.resume_parser import resume_parser
from app.services.ai.job_matcher import BM25Okapi, HybridJobMatcher
from app.services.ai.interview_evaluator import interview_evaluator
from app.services.ai.question_generator import question_generator

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_smarthire.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
db = TestingSessionLocal()
seed_database(db)
db.close()

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_auth_registration_and_login():
    import uuid
    email = f"testuser_{uuid.uuid4().hex[:6]}@smarthire.ai"
    password = "SecurePassword123!"
    
    # 1. Register
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test Candidate",
        "target_role": "Backend Developer",
        "language_preference": "English"
    })
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert "access_token" in data
    assert data["user"]["email"] == email

    # 2. Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

def test_resume_parser_entity_extraction():
    sample_text = """
    Aarav Sharma
    aarav@example.com | +91 98765 43210
    Software Engineer with experience in Python, FastAPI, Docker, and PostgreSQL.
    Projects:
    Built microservice APIs using FastAPI, Redis caching, and Docker.
    Education:
    Bachelor of Technology in Computer Science, 2023.
    """
    parsed = resume_parser.parse_resume_text(sample_text)
    assert parsed["name"] == "Aarav Sharma"
    assert parsed["email"] == "aarav@example.com"
    skills = [s.lower() for s in parsed["skills"]]
    assert "python" in skills
    assert "fastapi" in skills
    assert "docker" in skills
    assert "postgresql" in skills

def test_hybrid_job_matcher():
    corpus = [
        ["python", "fastapi", "docker", "redis", "postgresql", "backend"],
        ["react", "typescript", "tailwind", "nextjs", "frontend"],
        ["machine", "learning", "pytorch", "pandas", "data"]
    ]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(["python", "fastapi", "backend"])
    assert scores[0] > scores[1]
    assert scores[0] > scores[2]

def test_interview_evaluator_hinglish_detection():
    hinglish_text = "Sir mujhe lagta hai ki REST API basically client aur server ke beech communication ke liye use hoti hai."
    lang = interview_evaluator.detect_language(hinglish_text)
    assert lang == "Hinglish"

    english_text = "REST APIs use HTTP methods like GET and POST to transfer data between client and server."
    lang2 = interview_evaluator.detect_language(english_text)
    assert lang2 == "English"

@pytest.mark.anyio
async def test_question_generator():
    q_data = await question_generator._generate_contextual_question(
        candidate_name="Aarav",
        target_role="Backend Developer",
        skills=["Python", "FastAPI"],
        skill_gaps=["System Design"],
        projects=[{"title": "Task Queue Microservice"}],
        previous_qa=[],
        language="English",
        sequence=1
    )
    assert "question" in q_data
    assert "Task Queue Microservice" in q_data["question"]
    assert q_data["category"] == "technical"
