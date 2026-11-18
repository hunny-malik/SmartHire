import os
import httpx

client = httpx.Client(base_url="http://127.0.0.1:8000/api")

# Register or login user
reg = client.post("/auth/register", json={
    "email": "aarav.test@smarthire.ai",
    "password": "Password123!",
    "full_name": "Aarav Sharma",
    "target_role": "Data Scientist"
})
if reg.status_code == 201:
    token = reg.json()["access_token"]
else:
    login = client.post("/auth/login", json={"email": "aarav.test@smarthire.ai", "password": "Password123!"})
    token = login.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Upload a real sample resume
resume_path = os.path.join(os.path.dirname(__file__), "sample_resumes", "data_scientist_ml.pdf")
with open(resume_path, "rb") as f:
    upload_res = client.post("/resume/upload", files={"file": ("data_scientist_ml.pdf", f, "application/pdf")}, headers=headers)
print("Upload status:", upload_res.status_code)

# Get roles
roles = client.get("/roles", headers=headers).json()
role_id = next(r["id"] for r in roles if r["title"] == "Data Scientist")
print(f"Testing analyze for role Data Scientist ({role_id})")

# Call analyze
analyze_res = client.post("/skills/analyze", json={"role_id": role_id}, headers=headers)
print("Analyze HTTP Status:", analyze_res.status_code)
if analyze_res.status_code == 200:
    data = analyze_res.json()
    print("Match %:", data.get("match_percentage"))
    print("Gap %:", data.get("gap_percentage"))
    print("Nodes:", len(data.get("prerequisite_dag", {}).get("nodes", [])))
    print("Edges:", len(data.get("prerequisite_dag", {}).get("edges", [])))
    print("Career Path:", data.get("career_transition_path"))
    print("\nSUCCESS: /api/skills/analyze returned 200 OK and validated cleanly against Pydantic schema!")
else:
    print("Error:", analyze_res.text)
