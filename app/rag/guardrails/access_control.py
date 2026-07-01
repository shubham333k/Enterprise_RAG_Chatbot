"""
Role-Based Access Control (RBAC) for document retrieval.
Access filters are applied at the VECTOR SEARCH level — restricted chunks
never reach the LLM context (not just hidden in the UI).
"""
from typing import List, Optional


# Access level hierarchy per role (from the blueprint)
ROLE_ACCESS_MAP = {
    "admin":       ["public", "hr", "engineering", "sales", "legal", "finance"],
    "hr":          ["public", "hr"],
    "engineering": ["public", "engineering"],
    "sales":       ["public", "sales"],
    "employee":    ["public"],
}


def get_allowed_access_levels(role: str) -> List[str]:
    """Return the list of access levels a role can see."""
    return ROLE_ACCESS_MAP.get(role.lower(), ["public"])


def build_chroma_filter(role: str) -> Optional[dict]:
    """
    Build a ChromaDB `where` filter for the given role.
    ChromaDB supports $in operator for list membership.
    
    Returns None if all levels are allowed (admin) — no filter needed.
    """
    allowed = get_allowed_access_levels(role)
    
    # Admin sees everything — no filter
    if set(allowed) >= set(ROLE_ACCESS_MAP["admin"]):
        return None

    if len(allowed) == 1:
        return {"access_level": {"$eq": allowed[0]}}
    else:
        return {"access_level": {"$in": allowed}}


def can_access_document(role: str, access_level: str) -> bool:
    """Check if a role can access a document with the given access level."""
    allowed = get_allowed_access_levels(role)
    return access_level.lower() in allowed
