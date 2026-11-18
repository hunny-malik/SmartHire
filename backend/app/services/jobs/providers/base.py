from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseJobProvider(ABC):
    """
    Abstract base interface for all external and internal job aggregation providers.
    """
    @abstractmethod
    async def search_jobs(
        self, 
        query: str, 
        location: Optional[str] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search live job opportunities. Returns standardized job dictionaries:
        [{
            "external_id": str,
            "title": str,
            "company": str,
            "location": str,
            "job_type": str,
            "salary_range": Optional[str],
            "experience_level": str,
            "required_skills": List[str],
            "description": str,
            "apply_url": str,
            "source": str,
            "posted_date": str
        }]
        """
        pass
