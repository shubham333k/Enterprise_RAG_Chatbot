"""
Query pipeline.
Flow: Question → Embed → Vector Search (RBAC filtered) → Generate Answer → Citations
"""
import time
import logging
from typing import Dict, Any

from app.rag.embeddings.embedder import embedder
from app.rag.vectorstores.chroma_store import vector_store
from app.rag.guardrails.access_control import build_chroma_filter
from app.rag.guardrails.hallucination_checks import filter_low_quality_chunks
from app.rag.generation.answer_generator import generate_answer
from app.rag.generation.citations import build_citations
from app.api.core.config import settings

logger = logging.getLogger(__name__)


def run_query_pipeline(
    question: str,
    user_role: str = "employee",
    session_id: str = "default",
    top_k: int = None,
) -> Dict[str, Any]:
    """
    End-to-end RAG query pipeline with RBAC filtering.

    Steps:
    1. Embed the question (local, fast)
    2. Search ChromaDB with access-level filter (RBAC at DB level)
    3. Filter low-quality chunks (groundedness)
    4. Call cloud LLM (OpenAI GPT-4.1-mini)
    5. Build citations from retrieved chunks
    6. Return structured response

    Args:
        question: The user's question.
        user_role: Role from JWT (admin/hr/engineering/sales/employee).
        session_id: Chat session identifier.
        top_k: Number of chunks to retrieve.

    Returns:
        {
            "answer": str,
            "citations": list,
            "latency_ms": int,
            "session_id": str,
            "sources_found": int,
            "has_answer": bool,
        }
    """
    start_time = time.time()
    top_k = top_k or settings.TOP_K_DEFAULT

    # 1. Embed query
    try:
        query_vector = embedder.embed_query(question)
    except Exception as e:
        logger.error(f"Query embedding failed: {e}")
        return _error_response(session_id, "Failed to process your question.")

    # 2. RBAC filter — access control happens HERE, at retrieval, not at display
    access_filter = build_chroma_filter(user_role)
    logger.info(f"Querying as role='{user_role}', filter={access_filter}, top_k={top_k}")

    # 3. Vector search
    try:
        chunks = vector_store.search(
            query_embedding=query_vector,
            n_results=top_k,
            where=access_filter,
        )
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return _error_response(session_id, "Search error. Please try again.")

    # 4. Filter low-quality matches
    chunks = filter_low_quality_chunks(chunks, min_score=0.25)
    logger.info(f"Retrieved {len(chunks)} quality chunks for query")

    # 5. Generate answer via cloud LLM
    generation_result = generate_answer(question, chunks)

    # 6. Build citations
    citations = build_citations(generation_result["raw_chunks"])

    latency_ms = int((time.time() - start_time) * 1000)
    logger.info(f"Query completed in {latency_ms}ms | has_answer={generation_result['has_answer']}")

    return {
        "answer": generation_result["answer"],
        "citations": citations,
        "latency_ms": latency_ms,
        "session_id": session_id,
        "sources_found": len(citations),
        "has_answer": generation_result["has_answer"],
    }


def _error_response(session_id: str, message: str) -> Dict[str, Any]:
    return {
        "answer": message,
        "citations": [],
        "latency_ms": 0,
        "session_id": session_id,
        "sources_found": 0,
        "has_answer": False,
    }
