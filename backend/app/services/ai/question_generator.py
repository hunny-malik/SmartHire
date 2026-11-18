import json
import httpx
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.logging import logger

class QuestionSchema(BaseModel):
    question: str
    category: str = "technical" # technical, behavioral, situational, system_design
    difficulty: str = "medium" # easy, medium, hard
    skill: str = "Software Engineering"
    expected_concepts: List[str] = Field(default_factory=list)

class DynamicQuestionGenerator:
    """
    Generates dynamic interview questions tailored to candidate resume,
    target role, skill gaps, and previous turn answers with bilingual/Hinglish support.
    """
    @property
    def has_llm_key(self) -> bool:
        return bool(settings.OPENAI_API_KEY or settings.GEMINI_API_KEY)

    async def generate_question(
        self,
        candidate_name: str,
        target_role: str,
        skills: List[str],
        skill_gaps: List[str],
        projects: List[Dict[str, Any]],
        previous_qa: List[Dict[str, Any]],
        language: str = "English", # English, Hindi, Hinglish
        sequence: int = 1
    ) -> Dict[str, Any]:
        """
        Generates question via LLM API or contextual intelligent fallback.
        """
        # If API key is configured, call external LLM
        if self.has_llm_key:
            try:
                return await self._call_llm_api(
                    candidate_name, target_role, skills, skill_gaps, projects, previous_qa, language, sequence
                )
            except Exception as e:
                logger.warning(f"LLM API call failed ({e}); switching to contextual dynamic generator.")

        # High-fidelity contextual heuristic generation
        return self._generate_contextual_question(
            candidate_name, target_role, skills, skill_gaps, projects, previous_qa, language, sequence
        )

    def _generate_contextual_question(
        self,
        candidate_name: str,
        target_role: str,
        skills: List[str],
        skill_gaps: List[str],
        projects: List[Dict[str, Any]],
        previous_qa: List[Dict[str, Any]],
        language: str,
        sequence: int
    ) -> Dict[str, Any]:
        """
        Dynamic adaptive question builder based on user turn, resume projects,
        skills, identified gaps, and previous candidate answers.
        """
        import random
        is_hinglish = language.lower() in ["hinglish", "hindi"]

        # Extract context
        proj = projects[0] if projects else {}
        proj_title = proj.get("title", "")
        proj_desc = proj.get("description", "")
        proj_techs = proj.get("technologies", [])

        primary_skills = [s for s in skills if s not in ["HTML", "CSS", "Git"]] or ["Software Engineering", "APIs"]
        lead_skill = primary_skills[0] if primary_skills else "Python"
        sec_skill = primary_skills[1] if len(primary_skills) > 1 else "REST APIs"
        gap_skill = skill_gaps[0] if skill_gaps else "System Design"

        # Previous answer context
        last_answer = ""
        last_answer_lower = ""
        if previous_qa:
            last_answer = previous_qa[-1].get("candidate_answer", "")
            last_answer_lower = last_answer.lower()

        # Turn 1: Opening & Technical Project / Foundation
        if sequence == 1:
            opening_variants = []
            if proj_title:
                if is_hinglish:
                    opening_variants.append({
                        "question": f"Hello {candidate_name}! Welcome to your {target_role} mock interview. Aapke resume me '{proj_title}' project mention hai. Kya aap iska high-level architecture explain kar sakte hain aur aapne core technical choices kaise kiye?",
                        "category": "technical",
                        "difficulty": "medium",
                        "skill": lead_skill,
                        "expected_concepts": ["High-level architecture", "Component design", "Tech stack trade-offs", "Core responsibilities"]
                    })
                    opening_variants.append({
                        "question": f"Namaste {candidate_name}. Let's start with '{proj_title}'. Is project me sabse bada technical challenge kya tha aur aapne use kaise debug ya solve kiya?",
                        "category": "technical",
                        "difficulty": "medium",
                        "skill": lead_skill,
                        "expected_concepts": ["Problem definition", "Debugging approach", "Technical solution", "Result & learning"]
                    })
                else:
                    opening_variants.append({
                        "question": f"Welcome {candidate_name} to your {target_role} technical interview! Looking through your resume, I see your work on '{proj_title}'. Could you walk me through its high-level architecture and the key technical trade-offs you considered?",
                        "category": "technical",
                        "difficulty": "medium",
                        "skill": lead_skill,
                        "expected_concepts": ["High-level architecture", "Component design", "Tech stack trade-offs", "Core responsibilities"]
                    })
                    opening_variants.append({
                        "question": f"Hi {candidate_name}, glad to connect! In your work on '{proj_title}', what was the most complex technical hurdle you encountered, and how did you diagnose and overcome it?",
                        "category": "technical",
                        "difficulty": "medium",
                        "skill": lead_skill,
                        "expected_concepts": ["Root cause analysis", "Technical problem solving", "Validation", "Outcome"]
                    })
            else:
                if is_hinglish:
                    opening_variants.append({
                        "question": f"Hello {candidate_name}! Welcome to your {target_role} interview. Aapne {lead_skill} aur {sec_skill} par kaam kiya hai. Can you walk me through a complex technical problem that you solved using these technologies?",
                        "category": "technical",
                        "difficulty": "medium",
                        "skill": lead_skill,
                        "expected_concepts": [f"{lead_skill} best practices", "Architecture", "Design trade-offs", "Scalability"]
                    })
                else:
                    opening_variants.append({
                        "question": f"Welcome {candidate_name} to your {target_role} interview! With your experience in {lead_skill} and {sec_skill}, could you describe a significant engineering challenge you recently tackled and your step-by-step approach?",
                        "category": "technical",
                        "difficulty": "medium",
                        "skill": lead_skill,
                        "expected_concepts": [f"{lead_skill} best practices", "Architecture", "Design trade-offs", "Scalability"]
                    })

            selected = random.choice(opening_variants)
            return selected

        # Turn 2: Adaptive Follow-up based on candidate's actual answer
        if sequence == 2:
            # Check what candidate mentioned
            if any(term in last_answer_lower for term in ["database", "sql", "postgres", "mysql", "mongodb", "query", "index", "data"]):
                if is_hinglish:
                    q = f"Aapne database layer ka zikr kiya. Production me jab queries slow ho jati hain ya concurrent write locks create hote hain, toh aap database optimization, indexing aur connection pooling kaise approach karte hain?"
                else:
                    q = f"You touched upon the data layer. In production, how do you diagnose slow queries, optimize database indexing, and configure connection pooling to prevent deadlocks under heavy load?"
                return {
                    "question": q,
                    "category": "technical",
                    "difficulty": "hard",
                    "skill": "Database Optimization",
                    "expected_concepts": ["EXPLAIN query plan", "B-tree indexing", "Connection pool sizing", "Read replicas"]
                }
            elif any(term in last_answer_lower for term in ["api", "rest", "fastapi", "express", "backend", "microservice", "service"]):
                if is_hinglish:
                    q = f"Aapne APIs aur services explain kiye. Agar kisi upstream third-party service me intermittent failure ya high latency aaye, toh aap resilience ke liye circuit breakers, retries aur timeouts kaise implement karenge?"
                else:
                    q = f"Building on your API discussion: when an upstream external service suffers intermittent failures or latency spikes, how do you implement circuit breakers, exponential backoff, and idempotent retries to protect system stability?"
                return {
                    "question": q,
                    "category": "system_design",
                    "difficulty": "hard",
                    "skill": "Microservices & Resilience",
                    "expected_concepts": ["Circuit breaker pattern", "Exponential backoff", "Idempotency keys", "Fallback strategy"]
                }
            elif any(term in last_answer_lower for term in ["react", "frontend", "ui", "component", "state"]):
                if is_hinglish:
                    q = f"Frontend architecture me state management aur rendering performance kafi critical hote hain. Complex applications me unnecessary re-renders prevent karne aur initial page load time minimize karne ke liye aapki kya strategy hoti hai?"
                else:
                    q = f"In modern web applications, state synchronization and rendering efficiency are paramount. How do you prevent unnecessary component re-renders, optimize bundle size, and improve Core Web Vitals?"
                return {
                    "question": q,
                    "category": "technical",
                    "difficulty": "medium",
                    "skill": "Frontend Performance",
                    "expected_concepts": ["Memoization", "Code splitting", "State colocation", "Core Web Vitals"]
                }
            else:
                # Scaling & Concurrency follow-up
                if is_hinglish:
                    q = f"Great overview! Agar is system me traffic suddenly 10x badh jaye (thousands of concurrent requests/sec), toh aap bottlenecks kahan expect karte hain aur caching ya horizontal scaling kaise implement karenge?"
                else:
                    q = f"Now, suppose your architecture experiences a sudden 10x traffic surge (over 10,000 requests/sec). Where do you anticipate the first bottlenecks, and how would you implement caching, asynchronous queues, or horizontal autoscaling?"
                return {
                    "question": q,
                    "category": "system_design",
                    "difficulty": "hard",
                    "skill": "Scalability & Concurrency",
                    "expected_concepts": ["Distributed caching", "Message broker queue", "Stateless instances", "Horizontal autoscaling"]
                }

        # Turn 3: Target Role Core Competency & Skill Gap Challenge
        if sequence == 3:
            if is_hinglish:
                q = f"Target role '{target_role}' ke liye {gap_skill} ek critical requirement hai. Production environment me aap {gap_skill} ke core concepts ko implement karte waqt trade-offs aur reliability kaise ensure karenge?"
            else:
                q = f"For the '{target_role}' position, strong command over '{gap_skill}' is crucial. Could you walk me through a realistic scenario where you applied {gap_skill}, and how you handled edge cases or trade-offs?"
            return {
                "question": q,
                "category": "technical",
                "difficulty": "hard",
                "skill": gap_skill,
                "expected_concepts": [f"{gap_skill} core principles", "Production trade-offs", "Edge case mitigation", "Monitoring"]
            }

        # Turn 4: Incident Response, Debugging & Behavioral Scenarios
        if sequence == 4:
            behavioral_questions = []
            if is_hinglish:
                behavioral_questions.append({
                    "question": f"Aapke career me koi aisa real incident hua jab production me koi high-severity outage ya critical bug trigger hua ho? Aapne root cause isolate aur permanent fix deploy kaise kiya under pressure?",
                    "category": "behavioral",
                    "difficulty": "medium",
                    "skill": "Incident Response",
                    "expected_concepts": ["Root cause analysis", "Observability & logs", "Stakeholder communication", "Blameless post-mortem"]
                })
                behavioral_questions.append({
                    "question": f"Kabhi aisa hua ki aapka team member ya tech lead ke saath kisi technical architecture decision par disagreement ho? Aapne data aur reasoning se consensus kaise build kiya?",
                    "category": "behavioral",
                    "difficulty": "medium",
                    "skill": "Collaboration & Leadership",
                    "expected_concepts": ["Active listening", "Benchmarking & data", "Constructive compromise", "Team alignment"]
                })
            else:
                behavioral_questions.append({
                    "question": f"Could you tell me about a high-severity production outage or latency regression you personally investigated? How did you isolate the root cause, mitigate the immediate impact, and communicate with stakeholders?",
                    "category": "behavioral",
                    "difficulty": "medium",
                    "skill": "Incident Response",
                    "expected_concepts": ["Root cause analysis", "Observability & logs", "Stakeholder communication", "Blameless post-mortem"]
                })
                behavioral_questions.append({
                    "question": f"Describe a situation where you had a strong disagreement with a teammate or lead regarding technical design or framework selection. How did you validate your hypothesis and reach consensus?",
                    "category": "behavioral",
                    "difficulty": "medium",
                    "skill": "Collaboration & Leadership",
                    "expected_concepts": ["Data-driven decision making", "Active listening", "Constructive compromise", "Team alignment"]
                })

            selected = random.choice(behavioral_questions)
            return selected

        # Turn 5+: Final Wrap-up & Engineering Growth
        if is_hinglish:
            q = f"Final question: Rapidly evolving software industry me aap continuous learning, technical research aur clean coding standards maintain karne ke liye kya approach follow karte hain?"
        else:
            q = f"As our concluding question: In such a fast-evolving engineering landscape, how do you continuously upskill, evaluate new tools or libraries, and advocate for best engineering practices in your team?"

        return {
            "question": q,
            "category": "behavioral",
            "difficulty": "medium",
            "skill": "Continuous Learning & Engineering Culture",
            "expected_concepts": ["Mentorship", "Code review rigor", "Continuous learning", "Engineering standards"]
        }

    async def _call_llm_api(
        self,
        candidate_name: str,
        target_role: str,
        skills: List[str],
        skill_gaps: List[str],
        projects: List[Dict[str, Any]],
        previous_qa: List[Dict[str, Any]],
        language: str,
        sequence: int
    ) -> Dict[str, Any]:
        """
        External LLM API invocation with strict JSON schema parsing and retry safety.
        """
        # Formulate strict prompt
        prompt = f"""
You are an expert technical interviewer conducting a mock interview for the role of '{target_role}'.
Candidate Name: {candidate_name}
Candidate Skills: {', '.join(skills[:8])}
Candidate Skill Gaps to test: {', '.join(skill_gaps[:5])}
Recent Project: {projects[0].get('title') if projects else 'Full-stack application'}
Interview Sequence Order: Question {sequence}
Language: {language} (If Hindi or Hinglish, speak natural conversational Hinglish/Hindi code-switching).
Previous Turn History: {json.dumps(previous_qa[-2:] if previous_qa else [])}

Return STRICT JSON matching this exact structure:
{{
  "question": "The question to ask candidate",
  "category": "technical",
  "difficulty": "medium",
  "skill": "Relevant skill",
  "expected_concepts": ["concept1", "concept2", "concept3"]
}}
"""
        if settings.OPENAI_API_KEY:
            api_url = "https://api.openai.com/v1/chat/completions"
            api_key = settings.OPENAI_API_KEY
            model = "gpt-4o-mini"
        elif settings.GEMINI_API_KEY:
            api_url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
            api_key = settings.GEMINI_API_KEY
            model = "gemini-1.5-flash"
        else:
            raise ValueError("No LLM API key configured")

        # Call OpenAI / Gemini
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a professional technical interviewer who only outputs valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            res = await client.post(api_url, headers=headers, json=payload)
            if res.status_code == 200:
                raw_json = res.json()["choices"][0]["message"]["content"]
                parsed = json.loads(raw_json)
                return QuestionSchema(**parsed).model_dump()
            else:
                raise ValueError(f"LLM API returned status {res.status_code}: {res.text}")

question_generator = DynamicQuestionGenerator()
