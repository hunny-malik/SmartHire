from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.models.candidate_profile import CandidateProfile
from app.services.ai.embeddings import embedding_service
from app.core.logging import logger

class RoleMatcher:
    @staticmethod
    def match_candidate_to_roles(profile: CandidateProfile, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Calculates semantic match percentage between candidate profile and roles.
        Combines semantic embedding similarity with weighted skill coverage.
        """
        roles = db.query(Role).all()
        if not roles:
            return []

        cand_skills_set = {s.lower().strip() for s in (profile.skills or [])}
        cand_embedding = profile.embedding

        recommendations = []

        for role in roles:
            # 1. Skill overlap calculation
            role_skills = db.query(RoleSkill).filter(RoleSkill.role_id == role.id).all()
            total_weight = 0
            matched_weight = 0
            matched_names = []
            missing_names = []

            for rs in role_skills:
                skill_obj = db.query(Skill).filter(Skill.id == rs.skill_id).first()
                if not skill_obj:
                    continue
                w = rs.importance_weight
                total_weight += w
                sk_name = skill_obj.name
                if sk_name.lower().strip() in cand_skills_set:
                    matched_weight += w
                    matched_names.append(sk_name)
                else:
                    missing_names.append(sk_name)

            skill_coverage = (matched_weight / total_weight) if total_weight > 0 else 0.0

            # 2. Embedding semantic similarity
            semantic_sim = 0.5
            if cand_embedding and role.embedding:
                semantic_sim = embedding_service.cosine_similarity(cand_embedding, role.embedding)

            # Combined weighted match score: 60% skill coverage + 40% semantic affinity
            final_match = (0.60 * skill_coverage) + (0.40 * semantic_sim)
            match_percentage = round(final_match * 100, 1)

            # Contextual reasoning
            if match_percentage >= 80:
                reason = f"Excellent fit. Strong technical alignment across core competencies ({', '.join(matched_names[:3])})."
            elif match_percentage >= 60:
                reason = f"Good career transition opportunity. Core foundations match, gap in specialized requirements ({', '.join(missing_names[:2])})."
            else:
                reason = f"Stretch role. Requires foundational upskilling in {', '.join(missing_names[:3])}."

            recommendations.append({
                "role_id": role.id,
                "role_title": role.title,
                "category": role.category,
                "match_percentage": match_percentage,
                "matching_skills": matched_names,
                "missing_skills": missing_names,
                "reason": reason
            })

        # Sort descending by match percentage
        recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
        return recommendations[:limit]

role_matcher = RoleMatcher()
