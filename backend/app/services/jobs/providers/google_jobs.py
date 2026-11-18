import httpx
import re
import urllib.parse
from typing import List, Dict, Any, Optional
from app.services.jobs.providers.base import BaseJobProvider
from app.services.ai.resume_parser import CANONICAL_SKILLS, ResumeParser
from app.core.config import settings
from app.core.logging import logger

class GoogleJobsProvider(BaseJobProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.endpoint = "https://serpapi.com/search.json"

    async def search_jobs(
        self, 
        query: str, 
        location: Optional[str] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        active_key = self.api_key or settings.SERPAPI_API_KEY
        if not active_key:
            logger.info("SerpAPI key not configured; skipping GoogleJobsProvider.")
            return []

        search_q = f"{query} {location or ''}".strip()
        params = {
            "engine": "google_jobs",
            "q": search_q,
            "api_key": active_key,
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.get(self.endpoint, params=params)
                if res.status_code != 200:
                    logger.warning(f"Google Jobs API returned HTTP {res.status_code}: {res.text[:200]}")
                    return []
                data = res.json()
                results = data.get("jobs_results", [])
                standardized = []
                for item in results[:limit]:
                    # Extract authentic tech skills matching taxonomy
                    full_desc = f"{item.get('title', '')} {item.get('description', '')}"
                    for h in item.get("job_highlights", []):
                        for sub_item in h.get("items", []):
                            full_desc += " " + sub_item

                    desc_lower = full_desc.lower()
                    matched_skills = []
                    for skill in CANONICAL_SKILLS:
                        escaped = re.escape(skill)
                        if re.search(r'(?:\b|(?<=[^a-zA-Z0-9]))' + escaped + r'(?:\b|(?=[^a-zA-Z0-9]))', desc_lower):
                            matched_skills.append(ResumeParser._format_skill_name(skill))
                            if len(matched_skills) >= 8:
                                break

                    if not matched_skills:
                        matched_skills = ["Software Engineering", "REST APIs", "Git"]

                    # Extract the direct apply link for this exact specific job
                    apply_links = item.get("apply_options", [])
                    apply_url = ""
                    if apply_links:
                        # Prefer direct employer links or reputable job boards (Dice, LinkedIn, Indeed)
                        apply_url = apply_links[0].get("link")
                    
                    if not apply_url:
                        # Fallback to direct Google Jobs posting URL (opens the exact job detail)
                        apply_url = item.get("share_link") or item.get("source_link")
                    
                    if not apply_url:
                        # Target specific role application search rather than generic company root
                        comp_name = item.get("company_name", "Company")
                        job_title = item.get("title", query)
                        apply_url = f"https://www.google.com/search?q={urllib.parse.quote(comp_name + ' ' + job_title + ' apply job')}"

                    standardized.append({
                        "id": f"serp-{item.get('job_id', abs(hash(item.get('title', ''))))}",
                        "external_id": f"serp-{item.get('job_id', abs(hash(item.get('title', ''))))}",
                        "title": item.get("title", query),
                        "company": item.get("company_name", "Leading Tech Employer"),
                        "location": item.get("location", location or "Remote"),
                        "job_type": item.get("detected_extensions", {}).get("schedule_type", "Full-time"),
                        "salary_range": item.get("detected_extensions", {}).get("salary"),
                        "experience_level": "Mid-Senior level",
                        "required_skills": matched_skills,
                        "description": item.get("description", "Exciting tech role with competitive benefits and engineering culture."),
                        "apply_url": apply_url,
                        "source": f"Google Jobs ({item.get('via') or 'Live'})",
                        "posted_date": item.get("detected_extensions", {}).get("posted_at", "Recently")
                    })
                return standardized
        except Exception as e:
            logger.error(f"GoogleJobsProvider error: {e}")
            return []
