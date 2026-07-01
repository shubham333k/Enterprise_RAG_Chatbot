"""
Embedding service using SentenceTransformers (all-MiniLM-L6-v2).
~90 MB RAM, CPU-only, runs fine on 8 GB / no-GPU machines.
"""
from sentence_transformers import SentenceTransformer
from typing import List
from app.api.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Lightweight local embeddings.
    Model: all-MiniLM-L6-v2 — 384-dimensional vectors, ~90 MB RAM.
    """

    _instance = None  # singleton to avoid reloading

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.model_name = settings.EMBEDDING_MODEL
        self._initialized = True
        logger.info("Embedding model loaded successfully.")

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts. Returns list of 384-dim vectors."""
        if not texts:
            return []
        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            batch_size=32,
        )
        return vectors.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string."""
        vector = self.model.encode(
            [query],
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vector[0].tolist()


# Singleton instance — import this everywhere
embedder = EmbeddingService()
