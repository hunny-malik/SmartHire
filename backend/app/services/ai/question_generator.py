import json
import random
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.logging import logger

class QuestionSchema(BaseModel):
    question: str
    category: str = "technical"
    difficulty: str = "medium"
    skill: str = "Software Engineering"
    expected_concepts: List[str] = Field(default_factory=list)

# Role-specific question bank across sequences
ROLE_QUESTION_BANKS = {
    "Backend Developer": {
        "sequence_1": [
            ("Walk me through how you design high-throughput REST or gRPC APIs in production, including request validation and error handling.", "API Architecture", ["Request validation", "Status codes", "Error handling", "Statelessness"]),
            ("When architecting a new backend microservice, how do you decide on data modeling and separation of concerns?", "System Architecture", ["Domain-driven design", "Service boundaries", "ORM vs raw SQL", "Layered architecture"]),
            ("In your backend experience, how have you handled asynchronous processing and task queues for non-blocking requests?", "Asynchronous Processing", ["Message brokers", "Worker threads", "Event-driven design", "Dead-letter queues"])
        ],
        "sequence_2": [
            ("In production, when database queries encounter slow performance or lock contention, what is your diagnostic and indexing playbook?", "Database Optimization", ["EXPLAIN ANALYZE", "B-tree indexing", "Connection pool sizing", "Read replicas"]),
            ("How do you implement distributed caching with Redis, and how do you handle cache invalidation and cache stampedes?", "Caching Strategies", ["Cache-aside", "TTL strategies", "Mutual exclusion locks", "Eviction policies"]),
            ("When an upstream service becomes unresponsive or high-latency, how do you implement circuit breakers and retries with backoff?", "Fault Tolerance", ["Circuit breaker", "Exponential backoff", "Jitter", "Fallback responses"])
        ],
        "sequence_3": [
            ("How do you manage database transactions, ACID guarantees, and optimistic versus pessimistic locking in high-concurrency workflows?", "Database Concurrency", ["ACID properties", "Isolation levels", "Optimistic locking", "Deadlock resolution"]),
            ("Can you walk me through designing an idempotent endpoint for critical operations like payment or billing?", "Idempotency", ["Idempotency keys", "Atomic commits", "Distributed locks", "Two-phase commit"])
        ]
    },
    "Data Scientist": {
        "sequence_1": [
            ("Walk me through your typical end-to-end machine learning pipeline from exploratory data analysis to feature engineering.", "ML Pipeline", ["EDA", "Missing value imputation", "Feature scaling", "Feature selection"]),
            ("How do you handle class imbalance when training classification models in practical business scenarios?", "Class Imbalance", ["SMOTE", "Class weights", "Precision-Recall AUC", "Threshold tuning"]),
            ("Can you describe a challenging modeling project you built and how you validated that the model avoided overfitting?", "Model Validation", ["K-fold cross-validation", "Holdout sets", "Regularization", "Data leakage prevention"])
        ],
        "sequence_2": [
            ("How do you choose between tree-based ensembles (like XGBoost/LightGBM) and neural network architectures for tabular data?", "Algorithm Selection", ["Gradient boosting", "Feature interpretability", "Training latency", "Sample size trade-offs"]),
            ("In production, how do you detect and monitor for concept drift and data drift once an ML model is deployed?", "MLOps & Monitoring", ["Population stability index", "KS test", "Feature distribution tracking", "Model retraining triggers"]),
            ("Explain how you approach feature selection when dealing with high-dimensional datasets with strong multicollinearity.", "Feature Engineering", ["VIF", "L1 regularization", "PCA", "Feature importance"])
        ],
        "sequence_3": [
            ("How do you evaluate and tune trade-offs between precision, recall, and false positive rates based on specific business impact?", "Evaluation Metrics", ["ROC-AUC", "F1 score", "Cost-benefit matrix", "Confidence thresholds"]),
            ("When deploying an inference service, how do you optimize latency for batch vs real-time single-sample predictions?", "Model Serving", ["ONNX runtime", "Model quantization", "Batching", "Caching predictions"])
        ]
    },
    "Frontend Developer": {
        "sequence_1": [
            ("How do you structure component state and global store in large React or web applications to avoid unnecessary re-renders?", "State Architecture", ["State colocation", "Context API vs Redux/Zustand", "Memoization", "Render optimization"]),
            ("Can you explain your approach to modern responsive design and building accessible UI components that comply with WCAG standards?", "Web Accessibility", ["Semantic HTML", "ARIA roles", "Keyboard navigation", "Responsive typography"]),
            ("Walk me through how you optimize web application performance and bundle size to achieve green Core Web Vitals.", "Web Performance", ["Code splitting", "Lazy loading", "LCP / FID / CLS", "Tree shaking"])
        ],
        "sequence_2": [
            ("How do you manage client-side caching, data synchronization, and optimistic UI updates when consuming REST or GraphQL APIs?", "Data Fetching", ["React Query / SWR", "Cache invalidation", "Optimistic mutations", "Polling vs WebSockets"]),
            ("Explain the browser event loop, microtasks, macrotasks, and how they impact UI responsiveness and frame rates.", "Browser Internals", ["Call stack", "Microtask queue", "RequestAnimationFrame", "Event bubbling"]),
            ("How do you handle security vulnerabilities in frontend single-page apps, such as XSS, CSRF, and secure token storage?", "Frontend Security", ["Content Security Policy", "HttpOnly cookies", "Sanitization", "XSS defense"])
        ],
        "sequence_3": [
            ("When designing a shared design system or UI library, how do you handle component extensibility, theme tokens, and testing?", "Design Systems", ["Compound components", "CSS variables", "Snapshot tests", "Storybook isolation"]),
            ("How do you debug memory leaks and excessive DOM node trees in long-running single page applications?", "Performance Diagnostics", ["Chrome DevTools Memory tab", "Heap snapshots", "Event listener cleanup", "DOM recycling"])
        ]
    },
    "DevOps Engineer": {
        "sequence_1": [
            ("Walk me through how you architect an automated, zero-downtime CI/CD deployment pipeline from git commit to production.", "CI/CD Architecture", ["Build stages", "Automated testing", "Blue-Green / Canary", "Rollback triggers"]),
            ("How do you structure Infrastructure as Code using Terraform or CloudFormation to ensure modularity and state security?", "Infrastructure as Code", ["Remote state locking", "Module design", "Drift detection", "Immutable infrastructure"]),
            ("Can you explain how you design containerized application deployments for high availability in Kubernetes?", "Container Orchestration", ["Pod anti-affinity", "Readiness/Liveness probes", "Resource quotas", "HPA"])
        ],
        "sequence_2": [
            ("In production Kubernetes clusters, how do you configure ingress routing, TLS termination, and service mesh traffic control?", "Kubernetes Networking", ["Ingress controllers", "Cert-manager", "Mutual TLS", "Service mesh"]),
            ("How do you design a comprehensive observability stack spanning distributed tracing, metrics, and structured log aggregation?", "Observability", ["Prometheus & Grafana", "OpenTelemetry", "Log aggregation", "SLO / SLI definition"]),
            ("Walk me through how you implement automated secrets management and least-privilege IAM policies across multi-account cloud environments.", "Cloud Security", ["HashiCorp Vault", "IAM roles & policies", "Secrets rotation", "KMS encryption"])
        ],
        "sequence_3": [
            ("When investigating a sudden node memory pressure or cascading pod crashloop in production, what is your root-cause workflow?", "Troubleshooting", ["kubectl describe & logs", "OOMKilled diagnosis", "Cgroup limits", "Node drain"]),
            ("How do you plan and execute disaster recovery testing for multi-region or cross-cloud cloud infrastructure?", "Disaster Recovery", ["RTO and RPO", "Cross-region backups", "DNS failover", "Chaos engineering"])
        ]
    },
    "Fullstack Engineer": {
        "sequence_1": [
            ("Walk me through how you organize the contract and communication between frontend client layers and backend services.", "Fullstack Integration", ["API contracts", "TypeScript interfaces", "BFF pattern", "Error propagation"]),
            ("How do you balance server-side rendering versus client-side rendering depending on SEO, performance, and interactivity requirements?", "Rendering Strategies", ["SSR vs CSR vs SSG", "Hydration", "Initial page load", "Caching at edge"]),
            ("In a project you built, what was the most demanding feature spanning database modeling all the way to UI interaction?", "Fullstack Architecture", ["Data pipeline", "REST/GraphQL API", "State management", "UX responsiveness"])
        ],
        "sequence_2": [
            ("How do you implement secure end-to-end authentication with refresh tokens, CSRF protection, and session revocation?", "Auth Architecture", ["JWT vs session cookies", "Refresh token rotation", "CSRF tokens", "Revocation lists"]),
            ("When scaling an app from hundreds to tens of thousands of active users, what changes do you prioritize across frontend, API, and DB?", "Fullstack Scaling", ["CDN edge caching", "DB connection pooling", "Horizontal scaling", "Asset optimization"]),
            ("How do you approach automated testing across the full stack to ensure continuous delivery without brittle tests?", "Testing Strategy", ["Unit tests", "Integration tests", "E2E testing (Playwright)", "Mocking boundaries"])
        ],
        "sequence_3": [
            ("Can you discuss how you handle real-time bi-directional events (like live updates or notifications) across client and server?", "Real-Time Systems", ["WebSockets", "Server-Sent Events", "Pub/Sub backplane", "Reconnection logic"]),
            ("How do you coordinate zero-downtime database schema migrations when new features deploy concurrently with live user traffic?", "Database Migrations", ["Expand and contract pattern", "Backward compatibility", "Non-blocking index creation", "Rollback safety"])
        ]
    }
}

class DynamicQuestionGenerator:
    """
    Generates dynamic interview questions tailored to candidate resume,
    target role, skill gaps, and previous turn answers with bilingual/Hinglish support.
    """
    async def generate_question(
        self,
        candidate_name: str,
        target_role: str,
        skills: List[str],
        skill_gaps: List[str],
        projects: List[Dict[str, Any]],
        previous_qa: List[Dict[str, Any]],
        language: str = "English",
        sequence: int = 1
    ) -> Dict[str, Any]:
        """
        High-fidelity contextual dynamic question generation tailored by target role and user turn.
        """
        is_hinglish = language.lower() in ["hinglish", "hindi"]

        # Resolve role bucket
        matched_role_key = "Software Engineer"
        for key in ROLE_QUESTION_BANKS.keys():
            if key.lower() in target_role.lower() or target_role.lower() in key.lower():
                matched_role_key = key
                break
        if matched_role_key == "Software Engineer":
            matched_role_key = "Backend Developer"

        role_bank = ROLE_QUESTION_BANKS.get(matched_role_key, ROLE_QUESTION_BANKS["Backend Developer"])

        # Context details
        proj = projects[0] if projects else {}
        proj_title = proj.get("title", "")
        lead_skill = skills[0] if skills else "Software Engineering"
        gap_skill = skill_gaps[0] if skill_gaps else "System Design"

        last_answer = ""
        if previous_qa:
            last_answer = previous_qa[-1].get("candidate_answer", "").lower()

        # Turn 1: Opening & Role-Specific / Project Kickoff
        if sequence == 1:
            if proj_title:
                if is_hinglish:
                    q = f"Hello {candidate_name}! Welcome to your {target_role} mock interview. Aapke resume me '{proj_title}' project mention hai. Kya aap iska architecture explain kar sakte hain aur aapne core technical choices kaise kiye?"
                else:
                    q = f"Hello {candidate_name}, welcome to your {target_role} interview! In your work on '{proj_title}', what was the architectural structure and what key technical decisions did you make?"
                return {
                    "question": q,
                    "category": "technical",
                    "difficulty": "medium",
                    "skill": lead_skill,
                    "expected_concepts": ["High-level architecture", "Component design", "Tech stack trade-offs", "Core responsibilities"]
                }
            else:
                bank = role_bank.get("sequence_1", [])
                item = random.choice(bank)
                q_text = item[0]
                if is_hinglish:
                    q_text = f"Welcome {candidate_name} to your {target_role} round! {q_text} Aap Hinglish me comfortably explain kar sakte hain."
                return {
                    "question": q_text,
                    "category": "technical",
                    "difficulty": "medium",
                    "skill": item[1],
                    "expected_concepts": item[2]
                }

        # Turn 2: Follow-up adapting to user's answer or role deep-dive
        if sequence == 2:
            if any(term in last_answer for term in ["database", "sql", "postgres", "mysql", "mongodb", "query", "index"]):
                q = ("You highlighted the database layer. In production under high concurrency, how do you diagnose slow queries, optimize indexes, and configure connection pools to prevent lock contention?"
                     if not is_hinglish else
                     "Aapne database layer ka zikr kiya. Production me slow queries isolate karne, B-tree indexes optimize karne aur connection pooling configure karne ke liye aapka kya approach hota hai?")
                return {
                    "question": q,
                    "category": "technical",
                    "difficulty": "hard",
                    "skill": "Database Optimization",
                    "expected_concepts": ["EXPLAIN query plan", "B-tree indexing", "Connection pool sizing", "Read replicas"]
                }
            elif any(term in last_answer for term in ["api", "service", "rest", "fastapi", "express", "backend"]):
                q = ("Building on your services discussion: when an upstream external API experiences latency spikes or intermittent failures, how do you implement circuit breakers, retries with backoff, and fallbacks?"
                     if not is_hinglish else
                     "Aapne APIs aur services explain kiye. Agar kisi upstream external service me intermittent failure ya high latency aaye, toh aap circuit breakers, retries aur timeouts kaise implement karenge?")
                return {
                    "question": q,
                    "category": "system_design",
                    "difficulty": "hard",
                    "skill": "Fault Tolerance & Resilience",
                    "expected_concepts": ["Circuit breaker pattern", "Exponential backoff", "Idempotency keys", "Fallback strategy"]
                }
            elif any(term in last_answer for term in ["react", "component", "state", "frontend", "ui"]):
                q = ("In modern web applications, how do you prevent unnecessary component re-renders, manage asynchronous state, and optimize bundle size for Core Web Vitals?"
                     if not is_hinglish else
                     "Frontend architecture me unnecessary re-renders prevent karne, asynchronous state manage karne aur bundle size minimize karne ke liye aapki kya strategy hoti hai?")
                return {
                    "question": q,
                    "category": "technical",
                    "difficulty": "medium",
                    "skill": "Frontend Performance",
                    "expected_concepts": ["Memoization", "Code splitting", "State colocation", "Core Web Vitals"]
                }
            else:
                bank = role_bank.get("sequence_2", [])
                item = random.choice(bank)
                q_text = item[0]
                if is_hinglish:
                    q_text = f"Great! {q_text} Is scenario ko production context me explain karein."
                return {
                    "question": q_text,
                    "category": "system_design",
                    "difficulty": "hard",
                    "skill": item[1],
                    "expected_concepts": item[2]
                }

        # Turn 3: Target Role Skill Gap Challenge
        if sequence == 3:
            bank = role_bank.get("sequence_3", [])
            if bank and random.random() > 0.5:
                item = random.choice(bank)
                q_text = item[0]
                if is_hinglish:
                    q_text = f"Target role '{target_role}' ke liye: {q_text}"
                return {
                    "question": q_text,
                    "category": "technical",
                    "difficulty": "hard",
                    "skill": item[1],
                    "expected_concepts": item[2]
                }
            else:
                if is_hinglish:
                    q = f"Target role '{target_role}' ke liye {gap_skill} ek essential competency hai. Production environment me aap {gap_skill} ko implement karte waqt edge cases, trade-offs aur reliability kaise manage karte hain?"
                else:
                    q = f"For the '{target_role}' position, strong command over '{gap_skill}' is crucial. Could you walk me through a realistic scenario where you applied {gap_skill}, and how you handled edge cases or system trade-offs?"
                return {
                    "question": q,
                    "category": "technical",
                    "difficulty": "hard",
                    "skill": gap_skill,
                    "expected_concepts": [f"{gap_skill} core principles", "Production trade-offs", "Edge case mitigation", "Monitoring"]
                }

        # Turn 4: Incident Response & Engineering Culture
        if sequence == 4:
            behavioral_questions = [
                ("Could you tell me about a high-severity production outage or regression you personally diagnosed? How did you isolate root cause and communicate with stakeholders?",
                 "Aapke career me koi aisa incident jab production me koi high-severity outage ya critical bug trigger hua ho? Aapne root cause isolate aur permanent fix deploy kaise kiya under pressure?",
                 "Incident Response",
                 ["Root cause analysis", "Observability & logs", "Stakeholder communication", "Post-mortem"]),
                ("Describe a situation where you had a strong disagreement with a teammate or lead regarding technical design or framework selection. How did you validate your hypothesis and reach consensus?",
                 "Kabhi aisa hua ki aapka team member ya tech lead ke saath kisi technical architecture decision par disagreement ho? Aapne data aur reasoning se consensus kaise build kiya?",
                 "Collaboration & Leadership",
                 ["Data-driven decision making", "Active listening", "Constructive compromise", "Team alignment"])
            ]
            selected = random.choice(behavioral_questions)
            q_text = selected[1] if is_hinglish else selected[0]
            return {
                "question": q_text,
                "category": "behavioral",
                "difficulty": "medium",
                "skill": selected[2],
                "expected_concepts": selected[3]
            }

        # Turn 5+: Final Wrap-up
        if is_hinglish:
            q = f"As our concluding question for {target_role}: Rapidly evolving technology landscape me aap continuous learning aur clean engineering practices maintain karne ke liye kya approach follow karte hain?"
        else:
            q = f"As our concluding question for the {target_role} role: In such a fast-evolving engineering landscape, how do you continuously upskill, evaluate new tools, and advocate for best engineering practices in your team?"
        return {
            "question": q,
            "category": "behavioral",
            "difficulty": "medium",
            "skill": "Continuous Learning & Engineering Culture",
            "expected_concepts": ["Mentorship", "Code review rigor", "Continuous learning", "Engineering standards"]
        }

    async def _generate_contextual_question(
        self,
        candidate_name: str,
        target_role: str,
        skills: List[str],
        skill_gaps: List[str],
        projects: List[Dict[str, Any]],
        previous_qa: List[Dict[str, Any]],
        language: str = "English",
        sequence: int = 1
    ) -> Dict[str, Any]:
        return await self.generate_question(
            candidate_name=candidate_name,
            target_role=target_role,
            skills=skills,
            skill_gaps=skill_gaps,
            projects=projects,
            previous_qa=previous_qa,
            language=language,
            sequence=sequence
        )

question_generator = DynamicQuestionGenerator()
