"""
PDF document loader using PyMuPDF (fitz).
Extracts text page-by-page with page number metadata.
"""
import fitz  # PyMuPDF
from typing import List, Dict, Any
from pathlib import Path


def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Load a PDF and return a list of page dicts.
    
    Returns:
        List of {"page_number": int, "text": str, "source": str}
    """
    pages = []
    path = Path(file_path)

    try:
        doc = fitz.open(str(path))
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            if text:  # skip blank pages
                pages.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "source": path.name,
                    "file_path": str(path),
                    "file_type": "pdf",
                    "total_pages": len(doc),
                })
        doc.close()
    except Exception as e:
        raise ValueError(f"Failed to load PDF '{file_path}': {e}")

    return pages
