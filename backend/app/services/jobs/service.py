from typing import List, Dict, Any, Optional
from app.services.jobs.providers.base import BaseJobProvider
from app.services.jobs.providers.google_jobs import GoogleJobsProvider
from app.services.jobs.providers.fallback import FallbackJobProvider
from app.services.ai.job_matcher import hybrid_job_matcher
from app.models.candidate_profile import CandidateProfile
from app.core.logging import logger

class JobAggregationService:
    def __init__(self):
        self.providers: List[BaseJobProvider] = [
            GoogleJobsProvider(),
            FallbackJobProvider()
        ]

    async def get_recommended_jobs(
        self, 
        profile: CandidateProfile, 
        target_role: Optional[str] = None, 
        location: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        query = target_role or (profile.job_titles[0] if profile.job_titles else "Software Engineer")
        
        all_jobs: List[Dict[str, Any]] = []
        seen_keys = set()

        # Query active providers
        for provider in self.providers:
            try:
                jobs = await provider.search_jobs(query=query, location=location, limit=limit)
                for j in jobs:
                    key = (j.get("title", ""), j.get("company", ""))
                    if key not in seen_keys:
                        seen_keys.add(key)
                        all_jobs.append(j)
                if len(all_jobs) >= limit:
                    break
            except Exception as e:
                logger.error(f"Error fetching jobs from provider {provider.__class__.__name__}: {e}")

        # If external providers yielded no results, fallback will have filled or will fill
        if not all_jobs:
            fb = FallbackJobProvider()
            all_jobs = await fb.search_jobs(query=query, location=location, limit=limit)

        # Run hybrid ranking
        ranked = hybrid_job_matcher.rank_jobs(
            profile=profile,
            target_role=query,
            jobs=all_jobs
        )

        return ranked[:limit]

job_service = JobAggregationService()
