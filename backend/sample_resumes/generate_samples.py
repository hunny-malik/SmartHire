import os
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

SAMPLE_DATA = [
    {
        "filename_base": "junior_python_developer",
        "name": "Aarav Sharma",
        "email": "aarav.sharma@example.com",
        "phone": "+91 98765 43210",
        "title": "Junior Python & Backend Developer",
        "summary": "Passionate backend engineer with 1.5 years experience building scalable REST APIs with Python, FastAPI, and PostgreSQL. Eager to advance in Distributed Systems and System Design.",
        "skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker", "Git", "REST API", "HTML/CSS"],
        "education": [
            {"degree": "Bachelor of Technology in Computer Science", "institution": "Delhi Technological University", "year": "2023"}
        ],
        "experience": [
            {
                "title": "Junior Backend Developer",
                "company": "Nexus Web Solutions",
                "duration": "July 2023 - Present",
                "responsibilities": "Developed high-throughput REST APIs using FastAPI and SQLAlchemy. Integrated PostgreSQL relational database and optimized queries for customer management portal. Configured Docker containerization for local development and CI/CD."
            }
        ],
        "projects": [
            {
                "title": "Microservices Task Queue",
                "description": "Engineered asynchronous background job scheduler using FastAPI and Redis with real-time WebSocket notifications.",
                "technologies": ["Python", "FastAPI", "Redis", "Docker"]
            }
        ],
        "certifications": ["Python for Data Science - Coursera", "FastAPI Enterprise Mastery"]
    },
    {
        "filename_base": "senior_fullstack_engineer",
        "name": "Priya Nair",
        "email": "priya.nair@example.com",
        "phone": "+1 (415) 555-8921",
        "title": "Senior Full Stack Engineer",
        "summary": "Full Stack Architect with 6+ years building enterprise SaaS platforms using React, TypeScript, Python, FastAPI, PostgreSQL, and AWS.",
        "skills": ["Python", "JavaScript", "TypeScript", "React", "Next.js", "FastAPI", "PostgreSQL", "Redis", "Docker", "AWS", "System Design", "Low-Level Design", "CI/CD"],
        "education": [
            {"degree": "Master of Science in Software Engineering", "institution": "San Jose State University", "year": "2018"}
        ],
        "experience": [
            {
                "title": "Senior Full Stack Developer",
                "company": "OmniCloud Inc",
                "duration": "2021 - Present",
                "responsibilities": "Spearheaded frontend migration to Next.js with Tailwind CSS, reducing initial page load times by 42%. Architected scalable Python FastAPI microservices serving 2M daily active users on AWS ECS."
            }
        ],
        "projects": [
            {
                "title": "Real-Time Collaboration Canvas",
                "description": "Built multiplayer document editing system using WebSockets, React, and CRDT synchronization algorithms.",
                "technologies": ["React", "TypeScript", "Python", "Redis", "Docker"]
            }
        ],
        "certifications": ["AWS Certified Solutions Architect - Associate", "Certified Kubernetes Administrator (CKA)"]
    },
    {
        "filename_base": "data_scientist_ml",
        "name": "Rohan Verma",
        "email": "rohan.verma@example.com",
        "phone": "+91 98111 22334",
        "title": "Data Scientist & ML Researcher",
        "summary": "Machine Learning Engineer with 3 years experience developing computer vision, NLP models, and statistical predictive pipelines using PyTorch, Scikit-Learn, and Pandas.",
        "skills": ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Deep Learning", "PyTorch", "NLP", "Data Visualization", "Docker"],
        "education": [
            {"degree": "Master of Technology in Artificial Intelligence", "institution": "Indian Institute of Technology (IIT) Bombay", "year": "2021"}
        ],
        "experience": [
            {
                "title": "Data Scientist",
                "company": "DeepMetrics AI",
                "duration": "2021 - Present",
                "responsibilities": "Trained transformer-based NLP classification models achieving 94% precision. Developed automated feature engineering pipelines using Pandas, NumPy, and PyTorch for customer churn prediction."
            }
        ],
        "projects": [
            {
                "title": "Bilingual Medical Entity Recognizer",
                "description": "Fine-tuned multilingual RoBERTa model for automated clinical symptom extraction from patient consultations in Hindi and English.",
                "technologies": ["Python", "PyTorch", "Transformers", "NLP", "Docker"]
            }
        ],
        "certifications": ["Deep Learning Specialization - DeepLearning.AI", "TensorFlow Developer Certificate"]
    },
    {
        "filename_base": "devops_cloud_engineer",
        "name": "Marcus Chen",
        "email": "marcus.chen@example.com",
        "phone": "+1 (206) 555-0144",
        "title": "DevOps & Site Reliability Engineer",
        "summary": "Infrastructure engineer specializing in multi-cloud automation, Kubernetes cluster orchestration, Terraform IaC, and zero-downtime CI/CD delivery.",
        "skills": ["Linux", "Docker", "Kubernetes", "CI/CD", "Terraform", "AWS", "Prometheus & Grafana", "Python", "Bash", "Git"],
        "education": [
            {"degree": "Bachelor of Science in Computer Engineering", "institution": "University of Washington", "year": "2020"}
        ],
        "experience": [
            {
                "title": "DevOps Engineer",
                "company": "ScaleFleet Solutions",
                "duration": "2020 - Present",
                "responsibilities": "Automated infrastructure provisioning across 4 AWS regions using Terraform. Orchestrated 35+ microservice deployments on Amazon EKS Kubernetes clusters with Prometheus & Grafana alerting."
            }
        ],
        "projects": [
            {
                "title": "GitOps Automated Pipeline",
                "description": "Implemented ArgoCD GitOps pipeline enforcing automated security scanning, canary deployments, and rollback automation.",
                "technologies": ["Kubernetes", "Docker", "Terraform", "AWS", "CI/CD"]
            }
        ],
        "certifications": ["AWS Certified DevOps Engineer - Professional", "Certified Kubernetes Administrator (CKA)"]
    },
    {
        "filename_base": "react_frontend_developer",
        "name": "Ananya Joshi",
        "email": "ananya.joshi@example.com",
        "phone": "+91 97234 56789",
        "title": "Frontend React Developer",
        "summary": "Creative frontend developer with 2.5 years of expertise in crafting modern, responsive, accessible web interfaces using React, TypeScript, Next.js, and Tailwind CSS.",
        "skills": ["JavaScript", "TypeScript", "React", "Next.js", "HTML/CSS", "Tailwind CSS", "REST API", "Git"],
        "education": [
            {"degree": "Bachelor of Engineering in Information Technology", "institution": "Pune Institute of Computer Technology", "year": "2022"}
        ],
        "experience": [
            {
                "title": "Frontend Engineer",
                "company": "PixelCraft Studios",
                "duration": "2022 - Present",
                "responsibilities": "Built interactive user-facing dashboards using React 18, TypeScript, and Tailwind CSS. Implemented complex client-side state management, responsive charts, and optimized core web vitals."
            }
        ],
        "projects": [
            {
                "title": "Crypto Portfolio & Analytics Tracker",
                "description": "Developed interactive real-time crypto tracker with customizable widget dashboards and dark mode theme.",
                "technologies": ["React", "TypeScript", "Tailwind CSS", "REST API"]
            }
        ],
        "certifications": ["Meta Front-End Developer Professional Certificate"]
    }
]

def generate_pdf(data, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    y = height - 50

    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, data["name"])
    y -= 22
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#4B5563"))
    c.drawString(50, y, f"{data['title']} | {data['email']} | {data['phone']}")
    y -= 25

    # Divider
    c.setStrokeColor(colors.HexColor("#3B82F6"))
    c.setLineWidth(2)
    c.line(50, y, width - 50, y)
    y -= 20

    # Summary
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(50, y, "Professional Summary")
    y -= 16
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#374151"))
    # Wrap text roughly
    words = data["summary"].split()
    line = ""
    for w in words:
        if len(line + " " + w) < 95:
            line += " " + w
        else:
            c.drawString(50, y, line.strip())
            y -= 14
            line = w
    if line:
        c.drawString(50, y, line.strip())
        y -= 20

    # Skills
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(50, y, "Technical Skills")
    y -= 16
    c.setFont("Helvetica", 10)
    c.drawString(50, y, ", ".join(data["skills"]))
    y -= 22

    # Experience
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Work Experience")
    y -= 16
    for exp in data["experience"]:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"{exp['title']} - {exp['company']} ({exp['duration']})")
        y -= 14
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#374151"))
        c.drawString(60, y, exp["responsibilities"][:90])
        y -= 14
        if len(exp["responsibilities"]) > 90:
            c.drawString(60, y, exp["responsibilities"][90:180])
            y -= 16
        else:
            y -= 10

    # Projects
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(50, y, "Key Projects")
    y -= 16
    for proj in data["projects"]:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"{proj['title']} [Stack: {', '.join(proj['technologies'])}]")
        y -= 14
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#374151"))
        c.drawString(60, y, proj["description"][:95])
        y -= 20

    # Education
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#111827"))
    c.drawString(50, y, "Education")
    y -= 16
    for edu in data["education"]:
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"{edu['degree']} - {edu['institution']} ({edu['year']})")
        y -= 14

    c.save()

def generate_docx(data, output_path):
    doc = Document()
    doc.add_heading(data["name"], level=0)
    p = doc.add_paragraph(f"{data['title']} | {data['email']} | {data['phone']}")
    
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph(data["summary"])

    doc.add_heading("Technical Skills", level=1)
    doc.add_paragraph(", ".join(data["skills"]))

    doc.add_heading("Work Experience", level=1)
    for exp in data["experience"]:
        doc.add_heading(f"{exp['title']} at {exp['company']} ({exp['duration']})", level=2)
        doc.add_paragraph(exp["responsibilities"])

    doc.add_heading("Key Projects", level=1)
    for proj in data["projects"]:
        doc.add_heading(f"{proj['title']} ({', '.join(proj['technologies'])})", level=2)
        doc.add_paragraph(proj["description"])

    doc.add_heading("Education", level=1)
    for edu in data["education"]:
        doc.add_paragraph(f"{edu['degree']} - {edu['institution']} ({edu['year']})")

    doc.save(output_path)

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    for sample in SAMPLE_DATA:
        base_name = sample["filename_base"]
        pdf_path = os.path.join(out_dir, f"{base_name}.pdf")
        docx_path = os.path.join(out_dir, f"{base_name}.docx")
        generate_pdf(sample, pdf_path)
        generate_docx(sample, docx_path)
        print(f"Generated {base_name}.pdf and {base_name}.docx")
