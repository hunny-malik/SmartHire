from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.models.candidate_profile import CandidateProfile
from app.models.skill_gap import SkillGap, LearningRoadmap

# Curated high-yield resources aligned with ESCO skills
SKILL_RESOURCES = {
    "DSA": [
        {"title": "NeetCode 150 - Roadmap & Solutions", "url": "https://neetcode.io/practice", "type": "Interactive Practice", "est_hours": 20},
        {"title": "Grokking Algorithms", "url": "https://manning.com", "type": "Book", "est_hours": 15}
    ],
    "Advanced DSA": [
        {"title": "Graph Algorithms & Dynamic Programming", "url": "https://leetcode.com", "type": "Problem Sets", "est_hours": 25}
    ],
    "System Design": [
        {"title": "System Design Primer (Donne Martin)", "url": "https://github.com/donnemartin/system-design-primer", "type": "Open Source Guide", "est_hours": 25},
        {"title": "Designing Data-Intensive Applications", "url": "https://dataintensive.net", "type": "Textbook", "est_hours": 30}
    ],
    "Low-Level Design": [
        {"title": "Refactoring Guru - Design Patterns & SOLID", "url": "https://refactoring.guru", "type": "Interactive Guide", "est_hours": 15},
        {"title": "Clean Architecture by Robert C. Martin", "url": "https://clean-architecture.com", "type": "Book", "est_hours": 12}
    ],
    "Database Optimization": [
        {"title": "Use The Index, Luke (SQL Indexing)", "url": "https://use-the-index-luke.com", "type": "Guide", "est_hours": 10},
        {"title": "PostgreSQL Internals & Query Tuning", "url": "https://postgresql.org/docs", "type": "Documentation", "est_hours": 15}
    ],
    "Kubernetes": [
        {"title": "Kubernetes The Hard Way (Kelsey Hightower)", "url": "https://github.com/kelseyhightower/kubernetes-the-hard-way", "type": "Hands-on Lab", "est_hours": 18},
        {"title": "Official K8s Interactive Tutorials", "url": "https://kubernetes.io/docs/tutorials", "type": "Documentation", "est_hours": 12}
    ],
    "Docker": [
        {"title": "Docker for Developers", "url": "https://docker-curriculum.com", "type": "Hands-on Lab", "est_hours": 8}
    ],
    "Machine Learning": [
        {"title": "Scikit-Learn Machine Learning Course", "url": "https://scikit-learn.org", "type": "Tutorial", "est_hours": 20},
        {"title": "Fast.ai Practical Deep Learning", "url": "https://course.fast.ai", "type": "Course", "est_hours": 25}
    ],
    "PyTorch": [
        {"title": "PyTorch 60-Minute Blitz & Deep Learning", "url": "https://pytorch.org/tutorials", "type": "Hands-on Lab", "est_hours": 15}
    ],
    "LLM & RAG": [
        {"title": "Building RAG with Vector Databases", "url": "https://langchain.com", "type": "Architecture Guide", "est_hours": 15}
    ]
}

DEFAULT_RESOURCES = [
    {"title": "Comprehensive Core Mastery Course", "url": "https://freecodecamp.org", "type": "Interactive Course", "est_hours": 10},
    {"title": "Official Architecture Documentation & Best Practices", "url": "https://devdocs.io", "type": "Documentation", "est_hours": 8}
]

class SkillGapEngine:
    @staticmethod
    def analyze_skill_gap(profile: CandidateProfile, role: Role, db: Session) -> Dict[str, Any]:
        """
        Calculates gap, prerequisites DAG, and topologically sorted career transition path.
        """
        role_skills = db.query(RoleSkill).filter(RoleSkill.role_id == role.id).all()
        cand_skills_lower = {s.lower().strip() for s in (profile.skills or [])}

        matching_skills = []
        missing_skills_dict = {}
        total_importance = 0
        matched_importance = 0

        # All skills in DB to resolve prerequisites
        all_skills_db = {s.name: s for s in db.query(Skill).all()}

        for rs in role_skills:
            skill = all_skills_db.get(rs.skill.name if rs.skill else "")
            if not skill:
                continue
            
            w = rs.importance_weight
            total_importance += w

            is_matched = skill.name.lower().strip() in cand_skills_lower or any(
                skill.name.lower() in cs for cs in cand_skills_lower
            )

            if is_matched:
                matched_importance += w
                matching_skills.append({
                    "name": skill.name,
                    "level": rs.required_level,
                    "importance": w,
                    "category": skill.category
                })
            else:
                # Missing skill calculation
                gap_score = round(float(w * 10), 1)
                priority = "critical" if w >= 8 else ("high" if w >= 6 else "medium")
                
                resources = SKILL_RESOURCES.get(skill.name, DEFAULT_RESOURCES)
                est_time = 15 if w >= 8 else 10

                missing_skills_dict[skill.name] = {
                    "name": skill.name,
                    "current_level": "none",
                    "required_level": rs.required_level,
                    "gap_score": gap_score,
                    "importance": w,
                    "priority": priority,
                    "prerequisites": skill.prerequisites or [],
                    "recommended_resources": resources,
                    "estimated_learning_hours": est_time
                }

        match_pct = round((matched_importance / total_importance * 100), 1) if total_importance > 0 else 0.0
        gap_pct = round(100.0 - match_pct, 1)

        # Build Topological Sort / Prerequisite DAG
        missing_names = list(missing_skills_dict.keys())
        sorted_learning_path = SkillGapEngine._topological_sort(missing_names, all_skills_db)

        # Format DAG nodes and edges for interactive visualization
        dag_nodes = []
        dag_edges = []
        for name in missing_names:
            sk_info = missing_skills_dict[name]
            dag_nodes.append({
                "id": name,
                "label": name,
                "priority": sk_info["priority"],
                "importance": sk_info["importance"]
            })
            for prereq in sk_info["prerequisites"]:
                dag_edges.append({
                    "from": prereq,
                    "to": name
                })
                # If prereq isn't in nodes yet, add it as a foundational node
                if not any(n["id"] == prereq for n in dag_nodes):
                    dag_nodes.append({
                        "id": prereq,
                        "label": prereq,
                        "priority": "foundation",
                        "importance": 5
                    })

        missing_skills_list = [missing_skills_dict[n] for n in sorted_learning_path if n in missing_skills_dict]

        return {
            "role_id": role.id,
            "role_title": role.title,
            "match_percentage": match_pct,
            "gap_percentage": gap_pct,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills_list,
            "prerequisite_dag": {"nodes": dag_nodes, "edges": dag_edges},
            "career_transition_path": sorted_learning_path
        }

    @staticmethod
    def _topological_sort(skills: List[str], all_skills_db: Dict[str, Skill]) -> List[str]:
        """
        Topologically sorts skills so foundational skills and prerequisites appear first.
        """
        in_degree = {s: 0 for s in skills}
        adj = {s: [] for s in skills}

        for s in skills:
            skill_obj = all_skills_db.get(s)
            if skill_obj and skill_obj.prerequisites:
                for prereq in skill_obj.prerequisites:
                    if prereq in in_degree:
                        adj[prereq].append(s)
                        in_degree[s] += 1

        # Queue nodes with in_degree == 0
        queue = [s for s in skills if in_degree[s] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)
            for neighbor in adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If any remain due to unhandled cycles, append them
        for s in skills:
            if s not in result:
                result.append(s)

        return result

    @staticmethod
    def generate_roadmap_plan(user_id: str, role_id: str, missing_skills: List[Dict[str, Any]], db: Session):
        """
        Generates and persists a structured 6-week learning roadmap in the database.
        """
        # Clear existing roadmap for this user and role
        db.query(LearningRoadmap).filter(
            LearningRoadmap.user_id == user_id,
            LearningRoadmap.role_id == role_id
        ).delete()

        week = 1
        for item in missing_skills:
            phase_title = f"Week {week}: Mastering {item['name']}"
            roadmap_entry = LearningRoadmap(
                user_id=user_id,
                role_id=role_id,
                week_number=week,
                phase_title=phase_title,
                skill_name=item["name"],
                status="not_started",
                learning_resources=item["recommended_resources"],
                estimated_hours=item["estimated_learning_hours"]
            )
            db.add(roadmap_entry)
            week += 1
            if week > 6:
                break

        # Final capstone week
        if week <= 6:
            db.add(LearningRoadmap(
                user_id=user_id,
                role_id=role_id,
                week_number=week,
                phase_title=f"Week {week}: Comprehensive Mock Interviews & Capstone Project",
                skill_name="Mock Interviews & System Architecture",
                status="not_started",
                learning_resources=[{"title": "SmartHire AI Mock Interviews", "url": "/interview", "type": "Live Simulation", "est_hours": 10}],
                estimated_hours=10
            ))

        db.commit()

skill_gap_engine = SkillGapEngine()
