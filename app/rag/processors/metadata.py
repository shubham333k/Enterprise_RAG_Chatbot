"""
Metadata builder utility.
Constructs and validates the metadata dict attached to each chunk.
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def build_document_metadata(
    file_path: str,
    department: str = "public",
    access_level: str = "public",
    document_type: str = "document",
    uploaded_by: Optional[str] = None,
) -> dict:
    """Build metadata dict for a document at ingestion time."""
    path = Path(file_path)
    return {
        "file_name": path.name,
        "file_type": path.suffix.lstrip(".").lower(),
        "file_size_kb": int(path.stat().st_size / 1024) if path.exists() else 0,
        "department": department,
        "access_level": access_level,
        "document_type": document_type,
        "uploaded_by": uploaded_by or "system",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
