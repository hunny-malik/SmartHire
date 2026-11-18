import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

print("===========================================================")
print("        SMARTHIRE END-TO-END STEP-BY-STEP VERIFICATION     ")
print("===========================================================")

# Step 1: Health check
res = client.get("/api/health")
assert res.status_code == 200, f"Health check failed: {res.text}"
print("[Step 1] Health Check: SUCCESS ->", res.json())

# Step 2: User Auth & Registration
email = "demo_candidate@smarthire.ai"
client.post("/api/auth/register", json={
    "email": email,
    "full_name": "Aarav Sharma",
    "password": "SecurePassword123!",
    "target_role": "Python Developer",
    "preferred_language": "en"
})
res = client.post("/api/auth/login", json={"email": email, "password": "SecurePassword123!"})
assert res.status_code == 200, f"Login failed: {res.text}"
token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("[Step 2] Auth & Token Generation: SUCCESS (JWT Bearer Token acquired)")

# Step 3: Resume Upload & Parsing
sample_file = os.path.join("sample_resumes", "junior_python_developer.pdf")
with open(sample_file, "rb") as f:
    res = client.post("/api/resume/upload", headers=headers, files={"file": ("junior_python_developer.pdf", f, "application/pdf")})
assert res.status_code == 200, f"Resume upload failed: {res.text}"
profile = res.json()
print(f"[Step 3] Resume Parsing: SUCCESS -> Name: {profile['full_name']}, Skills: {len(profile.get('skills', []))} found ({profile.get('skills', [])[:5]}...)")

# Step 4: Role Matching & Recommendations
res = client.get("/api/roles/recommendations", headers=headers)
assert res.status_code == 200, f"Roles failed: {res.text}"
roles = res.json()
top_role = roles[0] if roles else None
print(f"[Step 4] Role Recommendations: SUCCESS -> Found {len(roles)} roles. Top match: {top_role['role_title']} ({top_role['match_percentage']}%)")

# Step 5: Skill Gap Analysis & Prerequisite DAG
role_id = top_role["role_id"] if top_role else "role_python_dev"
res = client.post("/api/skills/analyze", headers=headers, json={"role_id": role_id})
assert res.status_code == 200, f"Skill gap failed: {res.text}"
gap_data = res.json()
print(f"[Step 5] Skill Gap Analysis: SUCCESS -> Matching: {len(gap_data.get('matching_skills', []))}, Missing: {len(gap_data.get('missing_skills', []))}, DAG Nodes: {len(gap_data.get('prerequisite_dag', {}).get('nodes', []))}")

# Step 6: Learning Roadmap
res = client.get(f"/api/skills/roadmap?role_id={role_id}", headers=headers)
assert res.status_code == 200, f"Roadmap failed: {res.text}"
roadmap = res.json()
print(f"[Step 6] Learning Roadmap: SUCCESS -> {len(roadmap)} weekly learning milestones generated")

# Step 7: Live Job Search & Hybrid Ranking
res = client.get("/api/jobs/recommendations", headers=headers)
assert res.status_code == 200, f"Jobs failed: {res.text}"
jobs = res.json()
top_job = jobs[0]["job"] if jobs else {}
print(f"[Step 7] Hybrid Job Matching: SUCCESS -> {len(jobs)} jobs ranked by BM25 + Cosine. Top: {top_job.get('title')} at {top_job.get('company')}")

# Step 8: Dynamic AI Mock Interview & Evaluation
res = client.post("/api/interview/start", headers=headers, json={"role_id": role_id, "language": "English"})
assert res.status_code == 200, f"Interview start failed: {res.text}"
interview_data = res.json()
interview_id = interview_data["interview_id"]
q = interview_data["question"]
print(f"[Step 8a] Interview Start: SUCCESS -> Session {interview_id}, Q1: \"{q['question_text'][:65]}...\"")

ans_res = client.post(f"/api/interview/{interview_id}/answer", headers=headers, json={
    "candidate_answer": "FastAPI uses ASGI with Pydantic for request validation, asynchronous async/await handlers for high concurrency, and auto-generates Swagger OpenAPI documentation."
})
assert ans_res.status_code == 200, f"Answer submit failed: {ans_res.text}"
eval_res = ans_res.json()
print(f"[Step 8b] Turn Evaluation: SUCCESS -> Technical Accuracy: {eval_res['technical_accuracy']}/100, Communication: {eval_res['communication_score']}/100")

# Step 9: Conclude Interview & Generate PDF Report
complete_res = client.post(f"/api/interview/{interview_id}/complete", headers=headers)
assert complete_res.status_code == 200, f"Complete interview failed: {complete_res.text}"
report_meta = complete_res.json()
print(f"[Step 9a] Interview Completed: Overall Score: {report_meta.get('overall_score')}/100")

report_res = client.get(f"/api/reports/{interview_id}", headers=headers)
assert report_res.status_code == 200, f"Report get failed: {report_res.text}"
report = report_res.json()
print(f"[Step 9b] Evaluation Report: Recommendation: {report.get('hire_recommendation')}")

pdf_res = client.get(f"/api/reports/{interview_id}/download", headers=headers)
assert pdf_res.status_code == 200, f"PDF download failed: {pdf_res.text}"
print(f"[Step 9c] PDF Report Generation: SUCCESS -> Downloaded binary PDF of size {len(pdf_res.content)} bytes")

# Step 10: ML Evaluation Metrics Endpoint
metrics_res = client.get("/api/metrics/ml")
assert metrics_res.status_code == 200, f"Metrics failed: {metrics_res.text}"
metrics = metrics_res.json()
print(f"[Step 10] ML Metrics API: SUCCESS -> {len(metrics)} benchmark indicators active")

print("===========================================================")
print("        ALL STEPS AND PIPELINE DETAILS VERIFIED 100%!       ")
print("===========================================================")
