"""
DOCX document loader using python-docx.
Extracts paragraphs with section heading detection.
"""
from docx import Document
from typing import List, Dict, Any
from pathlib import Path


def load_docx(file_path: str) -> List[Dict[str, Any]]:
    """
    Load a DOCX file and return a list of section dicts.
    Paragraphs are grouped into ~page-sized chunks.

    Returns:
        List of {"page_number": int, "text": str, "section_heading": str, "source": str}
    """
    path = Path(file_path)
    pages = []
    current_heading = "Introduction"
    current_text_parts = []
    virtual_page = 1
    char_budget = 3000  # approximate chars per "page"
    accumulated = 0

    try:
        doc = Document(str(path))
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Detect headings
            if para.style.name.startswith("Heading"):
                # Flush current buffer
                if current_text_parts:
                    pages.append({
                        "page_number": virtual_page,
                        "text": "\n".join(current_text_parts),
                        "section_heading": current_heading,
                        "source": path.name,
                        "file_path": str(path),
                        "file_type": "docx",
                    })
                    virtual_page += 1
                    current_text_parts = []
                    accumulated = 0
                current_heading = text
            else:
                current_text_parts.append(text)
                accumulated += len(text)
                # Break into new virtual page if too long
                if accumulated >= char_budget:
                    pages.append({
                        "page_number": virtual_page,
                        "text": "\n".join(current_text_parts),
                        "section_heading": current_heading,
                        "source": path.name,
                        "file_path": str(path),
                        "file_type": "docx",
                    })
                    virtual_page += 1
                    current_text_parts = []
                    accumulated = 0

        # Flush remaining
        if current_text_parts:
            pages.append({
                "page_number": virtual_page,
                "text": "\n".join(current_text_parts),
                "section_heading": current_heading,
                "source": path.name,
                "file_path": str(path),
                "file_type": "docx",
            })

    except Exception as e:
        raise ValueError(f"Failed to load DOCX '{file_path}': {e}")

    return pages
