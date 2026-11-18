import json
import re
import httpx
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.logging import logger

class EvaluationSchema(BaseModel):
    technical_accuracy: float = Field(..., ge=0, le=100)
    communication_score: float = Field(..., ge=0, le=100)
    confidence_score: float = Field(..., ge=0, le=100)
    problem_solving_score: float = Field(..., ge=0, le=100)
    completeness_score: float = Field(..., ge=0, le=100)
    feedback: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)

class InterviewEvaluator:
    """
    Evaluates candidate answers across technical accuracy, communication,
    confidence, problem solving, and completeness, with bilingual/Hinglish understanding.
    """
    @property
    def has_llm_key(self) -> bool:
        return bool(settings.OPENAI_API_KEY or settings.GEMINI_API_KEY)

    async def evaluate_answer(
        self,
        question_text: str,
        expected_concepts: List[str],
        candidate_answer: str,
        target_role: str,
        target_skill: Optional[str] = None,
        language: str = "English"
    ) -> Dict[str, Any]:
        detected_lang = self.detect_language(candidate_answer)

        if self.has_llm_key:
            try:
                eval_res = await self._call_llm_eval(
                    question_text, expected_concepts, candidate_answer, target_role, target_skill, language
                )
                eval_res["detected_language"] = detected_lang
                return eval_res
            except Exception as e:
                logger.warning(f"LLM evaluation API failed ({e}); using heuristic evaluator fallback.")

        eval_res = self._heuristic_evaluate(
            question_text, expected_concepts, candidate_answer, target_role, target_skill, language, detected_lang
        )
        eval_res["detected_language"] = detected_lang
        return eval_res

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detects if text is English, Hindi (Devanagari), or Hinglish (Romanized Hindi).
        """
        # Devanagari script range
        if re.search(r'[\u0900-\u097F]', text):
            return "Hindi"
        
        # Hinglish romanized markers
        hinglish_markers = [
            "hai", "hoti", "hota", "karte", "karna", "mujhe", "lagta", "ke", "liye", 
            "aur", "karenge", "bhi", "hum", "aap", "kaise", "kya", "tha", "raha", "sakte"
        ]
        words = text.lower().split()
        match_count = sum(1 for w in words if w in hinglish_markers)
        if match_count >= 2 or (len(words) > 0 and (match_count / len(words)) >= 0.15):
            return "Hinglish"

        return "English"

    def _heuristic_evaluate(
        self,
        question_text: str,
        expected_concepts: List[str],
        answer: str,
        target_role: str,
        target_skill: Optional[str],
        preferred_lang: str,
        detected_lang: str
    ) -> Dict[str, Any]:
        """
        Multi-dimensional grading rubric evaluating answer substance, technical depth,
        vocabulary, structure, and articulation.
        """
        words = answer.strip().split()
        word_count = len(words)
        answer_lower = answer.lower()

        # Check for explicit "I don't know" / skips / non-answers
        non_answer_markers = [
            "i don't know", "i dont know", "dont know", "don't know", "no idea", 
            "not sure", "pata nahi", "mujhe nahi pata", "skip", "pass", "no clue", 
            "i do not know", "can't answer", "cannot answer", "i have no idea", "nahi pata",
            "no", "nope", "nah", "na", "nothing"
        ]
        cleaned_ans = re.sub(r'[^a-zA-Z\s]', '', answer_lower).strip()
        is_non_answer = (
            any(cleaned_ans == na for na in non_answer_markers)
            or any(cleaned_ans.startswith(na + " ") or cleaned_ans.endswith(" " + na) for na in [
                "i don't know", "i dont know", "dont know", "don't know", "no idea", 
                "not sure", "pata nahi", "mujhe nahi pata", "no clue", "i do not know"
            ])
            or (word_count <= 4 and any(na in cleaned_ans for na in ["dont know", "no idea", "not sure", "skip", "pass", "pata nahi"]))
        )

        if is_non_answer:
            missing = expected_concepts[:3] if expected_concepts else ["Core technical concepts"]
            return {
                "technical_accuracy": 0.0,
                "communication_score": 25.0,
                "confidence_score": 0.0,
                "problem_solving_score": 0.0,
                "completeness_score": 0.0,
                "feedback": f"No answer was provided or you stated you did not know. For a {target_role} role, this topic should be reviewed.",
                "strengths": ["Honest response."] if word_count <= 2 else ["Direct acknowledgment."],
                "weaknesses": [f"Unfamiliar with core topic: {target_skill or 'this question'}. Recommended revision: {', '.join(missing)}."]
            }

        # 1. Concept matching
        matched_concepts = []
        for concept in expected_concepts:
            c_terms = concept.lower().split()
            if any(term in answer_lower for term in c_terms if len(term) > 3):
                matched_concepts.append(concept)

        concept_ratio = (len(matched_concepts) / len(expected_concepts)) if expected_concepts else 0.5

        # Check specific tech terms
        tech_keywords = [
            "api", "database", "cache", "redis", "latency", "scale", "query", "index", 
            "microservice", "docker", "pipeline", "async", "lock", "transaction", "acid", "thread",
            "cluster", "kafka", "spark", "partition", "sharding", "replica", "distributed"
        ]
        kw_hits = sum(1 for kw in tech_keywords if kw in answer_lower)

        # Handle very brief answers with 0 concepts
        if word_count < 8 and not matched_concepts:
            return {
                "technical_accuracy": round(min(25.0, 10.0 + kw_hits * 3.0), 1),
                "communication_score": 40.0,
                "confidence_score": 30.0,
                "problem_solving_score": 20.0,
                "completeness_score": 15.0,
                "feedback": f"Your response was very brief and did not demonstrate technical depth on {', '.join(expected_concepts[:2]) if expected_concepts else 'the subject'}.",
                "strengths": ["Prompt reply."],
                "weaknesses": [f"Answer lacked technical detail. Review and practice explaining: {', '.join(expected_concepts[:2]) if expected_concepts else 'core concepts'}."]
            }

        # 2. Technical Accuracy (Grounded 0 to 95)
        base_tech = (concept_ratio * 70.0) + min(20.0, kw_hits * 2.5)
        tech_acc = min(95.0, max(20.0, base_tech))

        # 3. Communication Score
        comm_score = 60.0
        if word_count >= 30:
            comm_score += 20.0
        elif word_count < 15:
            comm_score -= 15.0

        if detected_lang in ["Hinglish", "Hindi"]:
            comm_score += 10.0

        comm_score = min(95.0, max(35.0, comm_score))

        # 4. Problem Solving & Structure
        reasoning_words = ["because", "therefore", "trade-off", "optimized", "bottleneck", "approach", "prevent", "kyunki", "isliye", "reason", "tradeoff", "architecture"]
        has_reasoning = any(rw in answer_lower for rw in reasoning_words)
        ps_score = min(94.0, max(30.0, 40.0 + (25.0 if has_reasoning else 5.0) + (concept_ratio * 25.0)))

        # 5. Confidence Score
        hedge_words = ["maybe", "i guess", "probably", "not sure", "pata nahi", "shayad", "might be"]
        has_hedges = any(hw in answer_lower for hw in hedge_words)
        conf_score = min(92.0, max(30.0, 75.0 - (25.0 if has_hedges else 0.0) + (10.0 if word_count > 25 else 0.0)))

        # 6. Completeness Score
        comp_score = min(95.0, max(25.0, (concept_ratio * 60.0) + min(35.0, word_count * 0.6)))

        # Strengths & Weaknesses
        strengths = []
        weaknesses = []

        if matched_concepts:
            strengths.append(f"Referenced key concepts: {', '.join(matched_concepts[:2])}.")
        if kw_hits >= 2:
            strengths.append("Used appropriate domain terminology.")
        if has_reasoning:
            strengths.append("Articulated clear cause-and-effect reasoning.")
        if not strengths and word_count >= 15:
            strengths.append("Communicated clearly.")

        missing_concepts = [c for c in expected_concepts if c not in matched_concepts]
        if missing_concepts:
            weaknesses.append(f"Could elaborate on: {', '.join(missing_concepts[:2])}.")
        if word_count < 20:
            weaknesses.append("Response was brief; consider supporting answers with concrete examples.")
        if has_hedges:
            weaknesses.append("Avoid tentative phrasing like 'maybe' or 'I guess' to communicate with stronger conviction.")
        if not weaknesses:
            weaknesses.append("Consider discussing architectural trade-offs or alternate design patterns.")

        # Dynamic, calibrated feedback based on accuracy
        if tech_acc >= 75.0:
            feedback = (
                f"Strong response! You addressed the core requirements and articulated key principles well. "
                f"{'Highlighted: ' + ', '.join(matched_concepts) if matched_concepts else 'Demonstrated clear technical intuition.'}"
            )
        elif tech_acc >= 40.0:
            feedback = (
                f"Adequate foundational answer. You touched on the topic, but need deeper technical specifics. "
                f"{'Covered: ' + ', '.join(matched_concepts) if matched_concepts else 'Consider elaborating on architecture, trade-offs, and metrics.'}"
            )
        else:
            feedback = (
                f"Your answer lacked technical depth and did not sufficiently cover expected concepts. "
                f"Focus on explaining concrete mechanisms, design choices, and real production examples."
            )

        return {
            "technical_accuracy": round(tech_acc, 1),
            "communication_score": round(comm_score, 1),
            "confidence_score": round(conf_score, 1),
            "problem_solving_score": round(ps_score, 1),
            "completeness_score": round(comp_score, 1),
            "feedback": feedback,
            "strengths": strengths,
            "weaknesses": weaknesses
        }

    async def _call_llm_eval(
        self,
        question_text: str,
        expected_concepts: List[str],
        answer: str,
        target_role: str,
        target_skill: Optional[str],
        language: str
    ) -> Dict[str, Any]:
        prompt = f"""
Evaluate this technical interview answer for the role of '{target_role}'.
Question: "{question_text}"
Expected Concepts: {json.dumps(expected_concepts)}
Candidate Answer: "{answer}"
Evaluation criteria:
- Technical Accuracy (0-100)
- Communication (0-100) - Note: Candidate may speak in English, Hindi, or Hinglish (code-switching); evaluate fluency and clarity fairly.
- Confidence (0-100)
- Problem Solving (0-100)
- Completeness (0-100)
- Feedback (Constructive 2-3 sentences)
- Strengths (List of 2-3 specific points)
- Weaknesses (List of 1-2 constructive areas)

Output strictly valid JSON matching this schema:
{{
  "technical_accuracy": 82.0,
  "communication_score": 78.0,
  "confidence_score": 80.0,
  "problem_solving_score": 85.0,
  "completeness_score": 75.0,
  "feedback": "...",
  "strengths": ["...", "..."],
  "weaknesses": ["..."]
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

        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a senior technical interviewer and evaluator. Always return strictly valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            res = await client.post(api_url, headers=headers, json=payload)
            if res.status_code == 200:
                raw = res.json()["choices"][0]["message"]["content"]
                parsed = json.loads(raw)
                return EvaluationSchema(**parsed).model_dump()
            else:
                raise ValueError(f"LLM API returned HTTP {res.status_code}: {res.text}")

interview_evaluator = InterviewEvaluator()
