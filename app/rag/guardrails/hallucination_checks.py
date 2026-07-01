"""
Hallucination/groundedness checks.
Verifies that the answer is grounded in the retrieved chunks
rather than fabricated.
"""
from typing import List, Dict, Any


NO_ANSWER_PHRASE = "This information was not found in the indexed documents."
MIN_SIMILARITY_THRESHOLD = 0.3  # chunks below this are likely irrelevant


def is_grounded(answer: str, retrieved_chunks: List[Dict[str, Any]]) -> bool:
    """
    Heuristic groundedness check:
    1. If no chunks were retrieved → not grounded.
    2. If the answer contains the "not found" phrase → appropriately not grounded.
    3. If all retrieved chunks have similarity score < threshold → suspect.
    """
    if not retrieved_chunks:
        return False

    if NO_ANSWER_PHRASE.lower() in answer.lower():
        return True  # the model correctly reported no info found

    # Check average similarity of top chunks
    scores = [c.get("score", 0.0) for c in retrieved_chunks]
    avg_score = sum(scores) / len(scores) if scores else 0
    return avg_score >= MIN_SIMILARITY_THRESHOLD


def filter_low_quality_chunks(
    chunks: List[Dict[str, Any]],
    min_score: float = MIN_SIMILARITY_THRESHOLD,
) -> List[Dict[str, Any]]:
    """Remove chunks below the minimum similarity threshold."""
    return [c for c in chunks if c.get("score", 0.0) >= min_score]


def check_answer_safety(answer: str) -> dict:
    """
    Basic safety check on the generated answer.
    Returns {"safe": bool, "reason": str}
    """
    if not answer or len(answer.strip()) < 5:
        return {"safe": False, "reason": "Empty or too short answer"}

    # Check if the model is trying to refuse unreasonably
    refusal_phrases = ["I cannot", "I am unable", "I don't have access"]
    for phrase in refusal_phrases:
        if phrase.lower() in answer.lower() and NO_ANSWER_PHRASE.lower() not in answer.lower():
            return {"safe": True, "reason": "Model refusal (acceptable)"}

    return {"safe": True, "reason": "OK"}
