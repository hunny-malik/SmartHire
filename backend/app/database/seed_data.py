from sqlalchemy.orm import Session
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.models.job import Job
from app.services.ai.embeddings import embedding_service
from app.core.logging import logger

STANDARDIZED_SKILLS = [
    # Core Fundamentals & Languages
    {"name": "Python", "category": "Programming", "esco_uri": "esco:skill:python-prog", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "JavaScript", "category": "Programming", "esco_uri": "esco:skill:javascript", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "TypeScript", "category": "Programming", "esco_uri": "esco:skill:typescript", "prerequisites": ["JavaScript"], "difficulty_level": "intermediate"},
    {"name": "Java", "category": "Programming", "esco_uri": "esco:skill:java-prog", "prerequisites": ["OOP"], "difficulty_level": "intermediate"},
    {"name": "C++", "category": "Programming", "esco_uri": "esco:skill:cpp-prog", "prerequisites": ["DSA"], "difficulty_level": "advanced"},
    {"name": "Go", "category": "Programming", "esco_uri": "esco:skill:golang", "prerequisites": ["DSA"], "difficulty_level": "intermediate"},
    {"name": "SQL", "category": "Databases", "esco_uri": "esco:skill:sql-db", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "HTML/CSS", "category": "Frontend", "esco_uri": "esco:skill:html-css", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "Git", "category": "DevOps", "esco_uri": "esco:skill:git-vcs", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "Networking", "category": "Architecture", "esco_uri": "esco:skill:networking", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "Operating Systems", "category": "Architecture", "esco_uri": "esco:skill:os-sys", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "HTTP Basics", "category": "Architecture", "esco_uri": "esco:skill:http", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "Databases", "category": "Databases", "esco_uri": "esco:skill:databases-foundations", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "JSON", "category": "Architecture", "esco_uri": "esco:skill:json-data", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "Caching Basics", "category": "Databases", "esco_uri": "esco:skill:caching-basics", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "Cloud Architecture", "category": "Cloud", "esco_uri": "esco:skill:cloud-arch", "prerequisites": ["Networking", "Linux"], "difficulty_level": "intermediate"},
    {"name": "Linear Algebra", "category": "Data Science", "esco_uri": "esco:skill:linear-algebra", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "Vector Databases", "category": "Databases", "esco_uri": "esco:skill:vector-db", "prerequisites": ["Databases"], "difficulty_level": "intermediate"},

    # Architecture & Fundamentals
    {"name": "OOP", "category": "Architecture", "esco_uri": "esco:skill:oop", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "DSA", "category": "Algorithms", "esco_uri": "esco:skill:data-structures", "prerequisites": ["OOP"], "difficulty_level": "intermediate"},
    {"name": "Advanced DSA", "category": "Algorithms", "esco_uri": "esco:skill:advanced-dsa", "prerequisites": ["DSA"], "difficulty_level": "advanced"},
    {"name": "Low-Level Design", "category": "Architecture", "esco_uri": "esco:skill:lld", "prerequisites": ["OOP", "DSA"], "difficulty_level": "intermediate"},
    {"name": "System Design", "category": "Architecture", "esco_uri": "esco:skill:system-design", "prerequisites": ["Low-Level Design", "Distributed Systems"], "difficulty_level": "advanced"},
    {"name": "Backend Architecture", "category": "Architecture", "esco_uri": "esco:skill:backend-arch", "prerequisites": ["System Design"], "difficulty_level": "advanced"},
    {"name": "API Design", "category": "Architecture", "esco_uri": "esco:skill:api-design", "prerequisites": ["REST API"], "difficulty_level": "intermediate"},
    {"name": "Distributed Systems", "category": "Architecture", "esco_uri": "esco:skill:distributed-sys", "prerequisites": ["Networking", "Operating Systems"], "difficulty_level": "advanced"},

    # Web & Frameworks
    {"name": "React", "category": "Frontend", "esco_uri": "esco:skill:react-ui", "prerequisites": ["JavaScript", "HTML/CSS"], "difficulty_level": "intermediate"},
    {"name": "Next.js", "category": "Frontend", "esco_uri": "esco:skill:nextjs", "prerequisites": ["React"], "difficulty_level": "intermediate"},
    {"name": "Node.js", "category": "Backend", "esco_uri": "esco:skill:nodejs", "prerequisites": ["JavaScript"], "difficulty_level": "intermediate"},
    {"name": "FastAPI", "category": "Backend", "esco_uri": "esco:skill:fastapi", "prerequisites": ["Python", "REST API"], "difficulty_level": "intermediate"},
    {"name": "Django", "category": "Backend", "esco_uri": "esco:skill:django", "prerequisites": ["Python", "SQL"], "difficulty_level": "intermediate"},
    {"name": "Spring Boot", "category": "Backend", "esco_uri": "esco:skill:spring-boot", "prerequisites": ["Java", "OOP"], "difficulty_level": "intermediate"},
    {"name": "REST API", "category": "Backend", "esco_uri": "esco:skill:rest-api", "prerequisites": ["HTTP Basics"], "difficulty_level": "beginner"},
    {"name": "GraphQL", "category": "Backend", "esco_uri": "esco:skill:graphql", "prerequisites": ["REST API"], "difficulty_level": "intermediate"},
    {"name": "Tailwind CSS", "category": "Frontend", "esco_uri": "esco:skill:tailwind", "prerequisites": ["HTML/CSS"], "difficulty_level": "beginner"},

    # Databases & Storage
    {"name": "PostgreSQL", "category": "Databases", "esco_uri": "esco:skill:postgres", "prerequisites": ["SQL"], "difficulty_level": "intermediate"},
    {"name": "MySQL", "category": "Databases", "esco_uri": "esco:skill:mysql", "prerequisites": ["SQL"], "difficulty_level": "intermediate"},
    {"name": "MongoDB", "category": "Databases", "esco_uri": "esco:skill:mongodb", "prerequisites": ["JSON", "Databases"], "difficulty_level": "intermediate"},
    {"name": "Redis", "category": "Databases", "esco_uri": "esco:skill:redis", "prerequisites": ["Caching Basics"], "difficulty_level": "intermediate"},
    {"name": "Database Optimization", "category": "Databases", "esco_uri": "esco:skill:db-opt", "prerequisites": ["SQL", "PostgreSQL"], "difficulty_level": "advanced"},

    # Cloud, DevOps & Infrastructure
    {"name": "Linux", "category": "DevOps", "esco_uri": "esco:skill:linux-sys", "prerequisites": [], "difficulty_level": "beginner"},
    {"name": "Docker", "category": "DevOps", "esco_uri": "esco:skill:docker-container", "prerequisites": ["Linux"], "difficulty_level": "intermediate"},
    {"name": "Kubernetes", "category": "DevOps", "esco_uri": "esco:skill:k8s", "prerequisites": ["Docker", "Networking"], "difficulty_level": "advanced"},
    {"name": "CI/CD", "category": "DevOps", "esco_uri": "esco:skill:ci-cd", "prerequisites": ["Git"], "difficulty_level": "intermediate"},
    {"name": "Terraform", "category": "DevOps", "esco_uri": "esco:skill:terraform-iac", "prerequisites": ["Cloud Architecture"], "difficulty_level": "advanced"},
    {"name": "AWS", "category": "Cloud", "esco_uri": "esco:skill:aws-cloud", "prerequisites": ["Networking", "Linux"], "difficulty_level": "intermediate"},
    {"name": "Azure", "category": "Cloud", "esco_uri": "esco:skill:azure-cloud", "prerequisites": ["Networking", "Linux"], "difficulty_level": "intermediate"},
    {"name": "GCP", "category": "Cloud", "esco_uri": "esco:skill:gcp-cloud", "prerequisites": ["Networking", "Linux"], "difficulty_level": "intermediate"},
    {"name": "Prometheus & Grafana", "category": "DevOps", "esco_uri": "esco:skill:observability", "prerequisites": ["Docker"], "difficulty_level": "intermediate"},

    # AI, ML & Data Science
    {"name": "Data Analysis", "category": "Data Science", "esco_uri": "esco:skill:data-analysis", "prerequisites": ["Python", "SQL"], "difficulty_level": "beginner"},
    {"name": "Pandas", "category": "Data Science", "esco_uri": "esco:skill:pandas-lib", "prerequisites": ["Python"], "difficulty_level": "beginner"},
    {"name": "NumPy", "category": "Data Science", "esco_uri": "esco:skill:numpy-lib", "prerequisites": ["Python"], "difficulty_level": "beginner"},
    {"name": "Scikit-Learn", "category": "Machine Learning", "esco_uri": "esco:skill:sklearn", "prerequisites": ["Python", "Pandas", "NumPy"], "difficulty_level": "intermediate"},
    {"name": "Machine Learning", "category": "Machine Learning", "esco_uri": "esco:skill:ml-algos", "prerequisites": ["Linear Algebra", "Scikit-Learn"], "difficulty_level": "intermediate"},
    {"name": "Deep Learning", "category": "Machine Learning", "esco_uri": "esco:skill:deep-learning", "prerequisites": ["Machine Learning", "PyTorch"], "difficulty_level": "advanced"},
    {"name": "PyTorch", "category": "Machine Learning", "esco_uri": "esco:skill:pytorch", "prerequisites": ["Python", "NumPy"], "difficulty_level": "intermediate"},
    {"name": "TensorFlow", "category": "Machine Learning", "esco_uri": "esco:skill:tensorflow", "prerequisites": ["Python", "NumPy"], "difficulty_level": "intermediate"},
    {"name": "NLP", "category": "AI", "esco_uri": "esco:skill:nlp", "prerequisites": ["Deep Learning", "Python"], "difficulty_level": "advanced"},
    {"name": "Computer Vision", "category": "AI", "esco_uri": "esco:skill:cv", "prerequisites": ["Deep Learning", "PyTorch"], "difficulty_level": "advanced"},
    {"name": "LLM & RAG", "category": "AI", "esco_uri": "esco:skill:llm-rag", "prerequisites": ["NLP", "Vector Databases"], "difficulty_level": "advanced"},
    {"name": "Power BI", "category": "Data Science", "esco_uri": "esco:skill:power-bi", "prerequisites": ["Data Analysis", "SQL"], "difficulty_level": "beginner"},
    {"name": "Tableau", "category": "Data Science", "esco_uri": "esco:skill:tableau", "prerequisites": ["Data Analysis", "SQL"], "difficulty_level": "beginner"},
    {"name": "Advanced Statistics", "category": "Data Science", "esco_uri": "esco:skill:adv-stats", "prerequisites": ["Data Analysis"], "difficulty_level": "intermediate"},
    {"name": "Data Visualization", "category": "Data Science", "esco_uri": "esco:skill:data-vis", "prerequisites": ["Python", "Pandas"], "difficulty_level": "beginner"},
    {"name": "Apache Spark", "category": "Data Engineering", "esco_uri": "esco:skill:spark", "prerequisites": ["Python", "SQL", "Distributed Systems"], "difficulty_level": "advanced"},
    {"name": "Apache Kafka", "category": "Data Engineering", "esco_uri": "esco:skill:kafka", "prerequisites": ["Distributed Systems"], "difficulty_level": "advanced"}
]

STANDARDIZED_ROLES = [
    {
        "title": "Software Engineer",
        "category": "Core Engineering",
        "description": "Designs, implements, tests, and deploys high-scale software applications and modular backend systems.",
        "min_experience_months": 12,
        "skills": [
            ("DSA", 9, "intermediate"), ("OOP", 8, "intermediate"), ("Python", 8, "intermediate"),
            ("SQL", 7, "intermediate"), ("System Design", 8, "advanced"), ("Low-Level Design", 7, "intermediate"),
            ("API Design", 8, "intermediate"), ("Git", 6, "beginner"), ("Unit Testing", 7, "intermediate")
        ]
    },
    {
        "title": "Backend Developer",
        "category": "Web & Cloud",
        "description": "Specializes in scalable API services, microservices architecture, database optimization, and cloud deployments.",
        "min_experience_months": 24,
        "skills": [
            ("Python", 9, "intermediate"), ("FastAPI", 9, "advanced"), ("PostgreSQL", 8, "intermediate"),
            ("Redis", 8, "intermediate"), ("Docker", 8, "intermediate"), ("System Design", 9, "advanced"),
            ("Database Optimization", 8, "advanced"), ("REST API", 9, "advanced"), ("CI/CD", 7, "intermediate")
        ]
    },
    {
        "title": "Frontend Developer",
        "category": "Web & UI",
        "description": "Crafts accessible, high-performance responsive web interfaces, complex interactive states, and design systems.",
        "min_experience_months": 12,
        "skills": [
            ("JavaScript", 9, "advanced"), ("TypeScript", 9, "intermediate"), ("React", 9, "advanced"),
            ("Next.js", 8, "intermediate"), ("HTML/CSS", 9, "advanced"), ("Tailwind CSS", 8, "intermediate"),
            ("REST API", 7, "intermediate")
        ]
    },
    {
        "title": "Full Stack Developer",
        "category": "Web & Cloud",
        "description": "End-to-end web engineering covering responsive frontend components, robust backend APIs, and database persistence.",
        "min_experience_months": 24,
        "skills": [
            ("JavaScript", 8, "intermediate"), ("TypeScript", 8, "intermediate"), ("React", 9, "intermediate"),
            ("Python", 8, "intermediate"), ("FastAPI", 8, "intermediate"), ("PostgreSQL", 8, "intermediate"),
            ("Docker", 7, "intermediate"), ("Git", 7, "intermediate"), ("REST API", 9, "intermediate")
        ]
    },
    {
        "title": "Data Analyst",
        "category": "Data & Analytics",
        "description": "Extracts actionable business intelligence, builds executive dashboards, analyzes trends, and models relational datasets.",
        "min_experience_months": 12,
        "skills": [
            ("SQL", 9, "advanced"), ("Python", 8, "intermediate"), ("Pandas", 9, "intermediate"),
            ("Power BI", 8, "intermediate"), ("Tableau", 8, "intermediate"), ("Advanced Statistics", 7, "intermediate"),
            ("Data Visualization", 9, "advanced"), ("Data Analysis", 9, "advanced")
        ]
    },
    {
        "title": "Data Scientist",
        "category": "AI & Data",
        "description": "Builds statistical models, machine learning algorithms, hypothesis testing, and analytical predictive pipelines.",
        "min_experience_months": 24,
        "skills": [
            ("Python", 9, "advanced"), ("Pandas", 9, "advanced"), ("NumPy", 8, "advanced"),
            ("Scikit-Learn", 9, "advanced"), ("Machine Learning", 9, "advanced"), ("Deep Learning", 7, "intermediate"),
            ("Advanced Statistics", 9, "advanced"), ("SQL", 8, "intermediate")
        ]
    },
    {
        "title": "Machine Learning Engineer",
        "category": "AI & Engineering",
        "description": "Productionizes ML models, implements model inference pipelines, feature stores, and deep learning architectures.",
        "min_experience_months": 24,
        "skills": [
            ("Python", 9, "advanced"), ("PyTorch", 9, "advanced"), ("Machine Learning", 9, "advanced"),
            ("Deep Learning", 9, "advanced"), ("Docker", 8, "intermediate"), ("FastAPI", 8, "intermediate"),
            ("NLP", 7, "intermediate"), ("CI/CD", 7, "intermediate")
        ]
    },
    {
        "title": "AI Engineer",
        "category": "AI & LLM",
        "description": "Builds modern Generative AI, RAG systems, LLM agents, vector semantic search pipelines, and agentic workflows.",
        "min_experience_months": 24,
        "skills": [
            ("Python", 9, "advanced"), ("LLM & RAG", 10, "advanced"), ("NLP", 9, "advanced"),
            ("PyTorch", 8, "intermediate"), ("FastAPI", 8, "intermediate"), ("Docker", 8, "intermediate"),
            ("Redis", 7, "intermediate"), ("System Design", 8, "intermediate")
        ]
    },
    {
        "title": "DevOps Engineer",
        "category": "Infrastructure",
        "description": "Automates continuous integration, infrastructure as code, container orchestration, monitoring, and cloud reliability.",
        "min_experience_months": 24,
        "skills": [
            ("Linux", 9, "advanced"), ("Docker", 9, "advanced"), ("Kubernetes", 9, "advanced"),
            ("CI/CD", 9, "advanced"), ("Terraform", 9, "advanced"), ("AWS", 9, "advanced"),
            ("Prometheus & Grafana", 8, "intermediate"), ("Python", 7, "intermediate")
        ]
    },
    {
        "title": "Cloud Architect",
        "category": "Infrastructure",
        "description": "Designs secure, resilient, high-availability multi-region enterprise cloud infrastructure and migration roadmaps.",
        "min_experience_months": 36,
        "skills": [
            ("AWS", 9, "advanced"), ("Azure", 8, "intermediate"), ("Terraform", 9, "advanced"),
            ("Kubernetes", 8, "advanced"), ("System Design", 9, "advanced"), ("Distributed Systems", 9, "advanced"),
            ("Linux", 8, "intermediate")
        ]
    },
    {
        "title": "Data Engineer",
        "category": "Data Infrastructure",
        "description": "Designs large-scale distributed ETL pipelines, stream processing frameworks, data lakes, and dimensional warehouses.",
        "min_experience_months": 24,
        "skills": [
            ("Python", 9, "advanced"), ("SQL", 9, "advanced"), ("Apache Spark", 9, "advanced"),
            ("Apache Kafka", 9, "advanced"), ("PostgreSQL", 8, "intermediate"), ("Docker", 8, "intermediate"),
            ("Distributed Systems", 8, "intermediate")
        ]
    },
    {
        "title": "Cybersecurity Specialist",
        "category": "Security",
        "description": "Protects organizational assets through threat modeling, vulnerability management, zero-trust architecture, and compliance.",
        "min_experience_months": 24,
        "skills": [
            ("Linux", 9, "advanced"), ("Python", 8, "intermediate"), ("Docker", 7, "intermediate"),
            ("Distributed Systems", 7, "intermediate"), ("AWS", 8, "intermediate")
        ]
    }
]

SAMPLE_JOBS = [
    {
        "external_id": "job-google-01",
        "title": "Senior Backend Software Engineer",
        "company": "Stripe",
        "location": "San Francisco, CA (Hybrid / Remote)",
        "job_type": "Full-time",
        "salary_range": "$175,000 - $220,000 / year",
        "experience_level": "Mid-Senior level",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "System Design", "API Design"],
        "description": "Stripe is seeking an experienced Backend Engineer to scale our global core payments orchestration infrastructure. You will design ultra-reliable APIs handling millions of financial transactions daily, optimize database query execution plans, and build fault-tolerant microservices.",
        "apply_url": "https://stripe.com/jobs",
        "source": "Google Jobs",
        "posted_date": "2 days ago"
    },
    {
        "external_id": "job-databricks-02",
        "title": "AI & Machine Learning Engineer",
        "company": "Databricks",
        "location": "New York, NY (Remote)",
        "job_type": "Full-time",
        "salary_range": "$185,000 - $235,000 / year",
        "experience_level": "Mid-Senior level",
        "required_skills": ["Python", "PyTorch", "LLM & RAG", "NLP", "Docker", "FastAPI", "Distributed Systems"],
        "description": "Databricks is accelerating the future of generative AI. We are looking for an ML Engineer to build production-grade Retrieval-Augmented Generation (RAG) pipelines, optimize model inference latencies, and deploy scalable foundation model services.",
        "apply_url": "https://databricks.com/company/careers",
        "source": "Google Jobs",
        "posted_date": "1 day ago"
    },
    {
        "external_id": "job-meta-03",
        "title": "Full Stack Engineer (React & Python)",
        "company": "Airbnb",
        "location": "San Francisco, CA (Hybrid)",
        "job_type": "Full-time",
        "salary_range": "$160,000 - $210,000 / year",
        "experience_level": "Mid level",
        "required_skills": ["React", "TypeScript", "Python", "FastAPI", "PostgreSQL", "Tailwind CSS", "REST API"],
        "description": "Join Airbnb to build world-class guest and host discovery journeys. You will partner with product designers to ship responsive, elegant frontend components in React & TypeScript, while architecting resilient backend microservices in Python.",
        "apply_url": "https://careers.airbnb.com",
        "source": "LinkedIn Jobs",
        "posted_date": "3 days ago"
    },
    {
        "external_id": "job-netflix-04",
        "title": "DevOps & Cloud Infrastructure Engineer",
        "company": "Netflix",
        "location": "Los Gatos, CA (Remote)",
        "job_type": "Full-time",
        "salary_range": "$190,000 - $250,000 / year",
        "experience_level": "Senior level",
        "required_skills": ["Kubernetes", "Docker", "Terraform", "AWS", "CI/CD", "Linux", "Prometheus & Grafana"],
        "description": "Help Netflix power seamless global streaming entertainment. We seek a DevOps engineer to manage massive multi-region Kubernetes clusters, codify cloud infrastructure using Terraform, and automate continuous deployment with zero downtime.",
        "apply_url": "https://jobs.netflix.com",
        "source": "Google Jobs",
        "posted_date": "Just now"
    },
    {
        "external_id": "job-snowflake-05",
        "title": "Data Analyst & Business Intelligence Specialist",
        "company": "Snowflake",
        "location": "Seattle, WA (Hybrid)",
        "job_type": "Full-time",
        "salary_range": "$125,000 - $160,000 / year",
        "experience_level": "Mid level",
        "required_skills": ["SQL", "Python", "Pandas", "Power BI", "Tableau", "Data Analysis", "Data Visualization"],
        "description": "Snowflake's Product Analytics team is seeking a Data Analyst to translate complex platform usage telemetry into actionable strategic insights, executive dashboards, and customer segmentation metrics.",
        "apply_url": "https://careers.snowflake.com",
        "source": "Google Jobs",
        "posted_date": "4 days ago"
    },
    {
        "external_id": "job-uber-06",
        "title": "Distributed Systems Software Engineer",
        "company": "Uber",
        "location": "Sunnyvale, CA",
        "job_type": "Full-time",
        "salary_range": "$170,000 - $215,000 / year",
        "experience_level": "Mid-Senior level",
        "required_skills": ["DSA", "OOP", "System Design", "Go", "Distributed Systems", "API Design", "PostgreSQL"],
        "description": "Uber's Mobility Core team is hiring software engineers to design high-throughput dispatch algorithms. You will solve challenging distributed consensus, load shedding, and data consistency problems under intense real-time traffic.",
        "apply_url": "https://uber.com/careers",
        "source": "LinkedIn Jobs",
        "posted_date": "3 days ago"
    },
    {
        "external_id": "job-vercel-07",
        "title": "Senior Frontend Engineer",
        "company": "Vercel",
        "location": "Remote (Global)",
        "job_type": "Full-time",
        "salary_range": "$150,000 - $190,000 / year",
        "experience_level": "Senior level",
        "required_skills": ["React", "Next.js", "TypeScript", "JavaScript", "HTML/CSS", "Tailwind CSS"],
        "description": "Vercel is making the web faster and more collaborative. We are seeking a Frontend Engineer passionate about Web Vitals, micro-frontends, server components, and developer experience.",
        "apply_url": "https://vercel.com/careers",
        "source": "Google Jobs",
        "posted_date": "5 days ago"
    },
    {
        "external_id": "job-spotify-08",
        "title": "Data Engineer (Spark & Kafka)",
        "company": "Spotify",
        "location": "New York, NY (Hybrid)",
        "job_type": "Full-time",
        "salary_range": "$165,000 - $205,000 / year",
        "experience_level": "Mid-Senior level",
        "required_skills": ["Apache Spark", "Apache Kafka", "Python", "SQL", "PostgreSQL", "Docker", "Distributed Systems"],
        "description": "Spotify processes billions of listening events per second. Join the Data Platform team to build reliable streaming ETL pipelines, manage Kafka brokers, and optimize distributed Spark data transformations.",
        "apply_url": "https://spotifyjobs.com",
        "source": "LinkedIn Jobs",
        "posted_date": "2 days ago"
    }
]

def seed_database(db: Session):
    """Seed skills, roles, and sample jobs idempotently."""
    logger.info("Checking database seeding...")

    # Seed Skills
    skill_map = {}
    existing_skills = {s.name: s for s in db.query(Skill).all()}
    for sk in STANDARDIZED_SKILLS:
        if sk["name"] not in existing_skills:
            skill_obj = Skill(
                name=sk["name"],
                category=sk["category"],
                esco_uri=sk["esco_uri"],
                prerequisites=sk["prerequisites"],
                difficulty_level=sk["difficulty_level"]
            )
            db.add(skill_obj)
            db.flush()
            skill_map[sk["name"]] = skill_obj
        else:
            skill_map[sk["name"]] = existing_skills[sk["name"]]

    db.commit()

    # Seed Roles
    existing_roles = {r.title: r for r in db.query(Role).all()}
    for ro in STANDARDIZED_ROLES:
        if ro["title"] not in existing_roles:
            # Generate semantic embedding for role
            role_summary = f"{ro['title']} ({ro['category']}). {ro['description']} Required: {', '.join([s[0] for s in ro['skills']])}"
            role_emb = embedding_service.get_embedding(role_summary)

            role_obj = Role(
                title=ro["title"],
                category=ro["category"],
                description=ro["description"],
                min_experience_months=ro["min_experience_months"],
                embedding=role_emb
            )
            db.add(role_obj)
            db.flush()

            # Associate RoleSkills
            for skill_name, weight, req_level in ro["skills"]:
                if skill_name in skill_map:
                    role_skill = RoleSkill(
                        role_id=role_obj.id,
                        skill_id=skill_map[skill_name].id,
                        importance_weight=weight,
                        required_level=req_level
                    )
                    db.add(role_skill)
        else:
            role_obj = existing_roles[ro["title"]]
            if not role_obj.embedding:
                role_summary = f"{ro['title']} ({ro['category']}). {ro['description']} Required: {', '.join([s[0] for s in ro['skills']])}"
                role_obj.embedding = embedding_service.get_embedding(role_summary)
                db.add(role_obj)

    db.commit()

    # Seed Sample Jobs
    existing_job_ids = {j.external_id for j in db.query(Job).all() if j.external_id}
    for j in SAMPLE_JOBS:
        if j["external_id"] not in existing_job_ids:
            job_obj = Job(
                external_id=j["external_id"],
                title=j["title"],
                company=j["company"],
                location=j["location"],
                job_type=j["job_type"],
                salary_range=j["salary_range"],
                experience_level=j["experience_level"],
                required_skills=j["required_skills"],
                description=j["description"],
                apply_url=j["apply_url"],
                source=j["source"],
                posted_date=j["posted_date"]
            )
            db.add(job_obj)

    db.commit()
    logger.info("Database seeding completed with 50+ standardized skills, 12 career roles, and live job opportunities.")
