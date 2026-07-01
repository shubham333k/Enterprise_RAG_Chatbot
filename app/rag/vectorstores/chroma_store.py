"""
ChromaDB vector store wrapper.
Persistent local storage in dev, can be swapped to Pinecone/Qdrant in prod.
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid
import logging
from app.api.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Wraps ChromaDB with cosine similarity search and RBAC filtering.
    """

    _instance = None  # singleton

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        logger.info(f"Initializing ChromaDB at: {settings.CHROMA_PERSIST_DIR}")
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
        self._initialized = True
        logger.info(f"ChromaDB collection '{settings.CHROMA_COLLECTION}' ready. "
                    f"Documents: {self.collection.count()}")

    def add_chunks(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> List[str]:
        """Add a batch of chunks to the collection. Returns the generated IDs."""
        ids = [str(uuid.uuid4()) for _ in texts]
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        return ids

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search with optional metadata filter (for RBAC).
        
        Returns:
            List of {"text": str, "metadata": dict, "score": float}
        """
        try:
            kwargs = {
                "query_embeddings": [query_embedding],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"],
            }
            if where:
                kwargs["where"] = where

            results = self.collection.query(**kwargs)

            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]

            return [
                {
                    "text": docs[i],
                    "metadata": metas[i],
                    "score": 1 - dists[i],  # cosine similarity (higher = better)
                }
                for i in range(len(docs))
            ]
        except Exception as e:
            logger.error(f"ChromaDB search error: {e}")
            return []

    def delete_by_document_id(self, document_id: int) -> int:
        """Delete all chunks belonging to a document. Returns deleted count."""
        try:
            results = self.collection.get(
                where={"document_id": document_id},
                include=["documents"],
            )
            ids = results.get("ids", [])
            if ids:
                self.collection.delete(ids=ids)
            return len(ids)
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return 0

    def count(self) -> int:
        """Total number of chunks in the collection."""
        return self.collection.count()

    def reset(self):
        """Delete and recreate the collection. USE WITH CAUTION."""
        self.client.delete_collection(settings.CHROMA_COLLECTION)
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
        logger.warning("ChromaDB collection reset.")


# Singleton instance
vector_store = VectorStore()
