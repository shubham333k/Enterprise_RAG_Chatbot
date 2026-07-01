"""
Citation builder: converts raw retrieved chunks into structured citation objects
matching the blueprint's citation format.
"""
from typing import List, Dict, Any


def build_citations(raw_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build citation list from retrieved chunks.

    Blueprint citation format:
    [Source: HR_Policy_2024.pdf, Page 12, Section 4.2]

    Returns:
        List of {"document", "page", "section", "excerpt", "score"}
    """
    citations = []
    seen = set()

    for chunk in raw_chunks:
        meta = chunk.get("metadata", {})
        document = meta.get("file_name", "Unknown")
        page = meta.get("page_number", None)
        section = meta.get("section_heading", None)
        score = round(chunk.get("score", 0.0), 3)

        # Deduplicate by document+page
        key = (document, page, section)
        if key in seen:
            continue
        seen.add(key)

        # Excerpt: first 200 chars of the chunk
        excerpt = chunk.get("text", "")[:200].strip()
        if len(chunk.get("text", "")) > 200:
            excerpt += "..."

        citations.append({
            "document": document,
            "page": page,
            "section": section,
            "excerpt": excerpt,
            "score": score,
            "department": meta.get("department", "public"),
        })

    return citations


def format_citation_text(citation: dict) -> str:
    """Format a single citation as a human-readable string."""
    parts = [f"Source: {citation['document']}"]
    if citation.get("page"):
        parts.append(f"Page {citation['page']}")
    if citation.get("section"):
        parts.append(f"Section: {citation['section']}")
    return " · ".join(parts)
