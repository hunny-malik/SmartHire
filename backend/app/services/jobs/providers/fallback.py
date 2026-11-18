import urllib.parse
from typing import List, Dict, Any, Optional
from app.services.jobs.providers.base import BaseJobProvider
from app.database.seed_data import SAMPLE_JOBS

class FallbackJobProvider(BaseJobProvider):
    """
    Development fallback provider.
    Serves realistic, structured tech industry jobs when external API keys
    (like SerpAPI or LinkedIn) are unconfigured.
    All jobs are explicitly labeled as Dev Fallback Data.
    """
    async def search_jobs(
        self, 
        query: str, 
        location: Optional[str] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        results = []
        q_lower = query.lower() if query else ""

        for job in SAMPLE_JOBS:
            # Score relevance
            relevance = 0
            if q_lower in job["title"].lower() or any(q_lower in s.lower() for s in job["required_skills"]):
                relevance += 2
            if location and location.lower() in job["location"].lower():
                relevance += 1

            job_copy = dict(job)
            job_copy["id"] = job.get("id") or job.get("external_id") or f"job-{len(results)}"
            job_copy["source"] = f"{job['source']} (Dev Fallback Provider)"
            
            # Ensure apply_url links to specific role application query
            comp = job.get("company", "Company")
            title = job.get("title", "Software Engineer")
            job_copy["apply_url"] = f"https://www.google.com/search?q={urllib.parse.quote(comp + ' ' + title + ' job openings apply')}"
            results.append((relevance, job_copy))

        # Sort by relevance, then slice limit
        results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in results[:limit]]
