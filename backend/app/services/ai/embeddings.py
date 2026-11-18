import re
import math
import zlib
import numpy as np
from typing import List, Union
from app.core.logging import logger

class EmbeddingService:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._st_model = None
        self._use_st = False

        # Attempt to load sentence-transformers if available
        try:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer('all-MiniLM-L6-v2')
            self._use_st = True
            logger.info("Loaded SentenceTransformer ('all-MiniLM-L6-v2') successfully.")
        except Exception as e:
            logger.info(f"SentenceTransformers not active ({e}); using high-fidelity normalized subword hash vectorizer fallback.")

    def get_embedding(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * self.dimension

        if self._use_st and self._st_model:
            try:
                emb = self._st_model.encode(text, convert_to_numpy=True)
                return emb.tolist()
            except Exception as e:
                logger.warning(f"SentenceTransformer encoding failed: {e}. Falling back to hash vectorizer.")

        return self._hash_vectorize(text)

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(t) for t in texts]

    def _hash_vectorize(self, text: str) -> List[float]:
        """
        High-dimensional subword and token semantic hash vectorizer.
        Generates deterministic 384-dimensional normalized dense vectors
        preserving lexical and n-gram semantic similarities.
        """
        cleaned = re.sub(r'[^a-zA-Z0-9\s+#.]', ' ', text.lower())
        tokens = cleaned.split()
        vec = np.zeros(self.dimension, dtype=np.float32)

        if not tokens:
            return vec.tolist()

        for token in tokens:
            # Word level hashing (deterministic across processes)
            h1 = zlib.crc32(token.encode('utf-8')) % self.dimension
            vec[h1] += 1.5

            # 3-gram character subwords for morphological root similarity
            if len(token) >= 3:
                for i in range(len(token) - 2):
                    sub = token[i:i+3]
                    h_sub = zlib.crc32(sub.encode('utf-8')) % self.dimension
                    vec[h_sub] += 0.8

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec.tolist()

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        sim = float(np.dot(a, b) / (norm_a * norm_b))
        return max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim))

embedding_service = EmbeddingService()
