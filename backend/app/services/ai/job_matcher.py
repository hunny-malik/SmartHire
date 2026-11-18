import math
import re
from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.services.ai.embeddings import embedding_service
from app.models.candidate_profile import CandidateProfile

class BM25Okapi:
    """
    Standard BM25 Okapi ranking implementation for exact keyword and skill matching.
    """
    def __init__(self, corpus: List[List[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = corpus
        self.corpus_size = len(corpus)
        self.avgdl = sum(len(doc) for doc in corpus) / (self.corpus_size or 1)
        self.doc_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}
        self._initialize()

    def _initialize(self):
        df = {}
        for document in self.corpus:
            frequencies = {}
            for word in document:
                frequencies[word] = frequencies.get(word, 0) + 1
            self.doc_freqs.append(frequencies)

            for word in frequencies:
                df[word] = df.get(word, 0) + 1

        for word, freq in df.items():
            # BM25 standard smoothed IDF
            self.idf[word] = math.log(1 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    def get_scores(self, query: List[str]) -> List[float]:
        scores = []
        for index, doc in enumerate(self.corpus):
            score = 0.0
            doc_len = len(doc)
            doc_freq = self.doc_freqs[index]
            for word in query:
                if word in doc_freq:
                    freq = doc_freq[word]
                    numerator = self.idf.get(word, 0.0) * freq * (self.k1 + 1)
                    denominator = freq + self.k1 * (1 - self.b + self.b * doc_len / (self.avgdl or 1))
                    score += numerator / (denominator or 1)
            scores.append(score)
        
        # Min-max normalize scores to [0.0, 1.0]
        max_s = max(scores) if scores else 0.0
        if max_s > 0:
            scores = [s / max_s for s in scores]
        return scores

class HybridJobMatcher:
    """
    Hybrid Job Ranking Service combining BM25 keyword weighting and dense vector Cosine Similarity.
    """
    def __init__(
        self, 
        bm25_weight: float = settings.BM25_WEIGHT, 
        cosine_weight: float = settings.COSINE_WEIGHT
    ):
        self.bm25_weight = bm25_weight
        self.cosine_weight = cosine_weight

    def rank_jobs(
        self, 
        profile: CandidateProfile, 
        target_role: str, 
        jobs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if not jobs:
            return []

        cand_skills = [s.lower().strip() for s in (profile.skills or [])]
        cand_text = f"{target_role} {' '.join(cand_skills)} {' '.join(profile.job_titles or [])}"
        cand_query_tokens = [w for w in re.findall(r'\b[a-zA-Z0-9+#.]+\b', cand_text.lower()) if len(w) > 1]

        # Prepare corpus for BM25
        corpus_tokens = []
        for j in jobs:
            job_str = f"{j.get('title', '')} {' '.join(j.get('required_skills', []))} {j.get('description', '')}"
            tokens = [w for w in re.findall(r'\b[a-zA-Z0-9+#.]+\b', job_str.lower()) if len(w) > 1]
            corpus_tokens.append(tokens)

        # 1. BM25 Exact Keyword Scores
        bm25 = BM25Okapi(corpus_tokens)
        bm25_scores = bm25.get_scores(cand_query_tokens)

        # 2. Dense Vector Cosine Similarity
        cand_emb = profile.embedding or embedding_service.get_embedding(cand_text)
        ranked_results = []

        cand_skills_set = set(cand_skills)

        for i, j in enumerate(jobs):
            job_text = f"{j.get('title', '')}. Required Skills: {', '.join(j.get('required_skills', []))}. {j.get('description', '')}"
            job_emb = embedding_service.get_embedding(job_text)
            
            cos_score = embedding_service.cosine_similarity(cand_emb, job_emb)
            bm25_score = bm25_scores[i]

            # Combine weighted hybrid score
            final_score = (self.bm25_weight * bm25_score) + (self.cosine_weight * cos_score)
            match_percentage = round(min(100.0, final_score * 100), 1)

            # Detect matched skills
            job_req_skills = j.get("required_skills", [])
            matched_skills = [
                s for s in job_req_skills 
                if s.lower().strip() in cand_skills_set or any(c in s.lower() for c in cand_skills)
            ]

            ranked_results.append({
                "job": j,
                "bm25_score": round(bm25_score * 100, 1),
                "cosine_score": round(cos_score * 100, 1),
                "final_score": match_percentage,
                "matched_skills": matched_skills,
                "is_live_external": "Google Jobs (Live API)" in j.get("source", "")
            })

        # Rank descending by final hybrid score
        ranked_results.sort(key=lambda x: x["final_score"], reverse=True)
        return ranked_results

hybrid_job_matcher = HybridJobMatcher()
