"""
Plain text file loader.
Splits by double newlines into virtual pages.
"""
from typing import List, Dict, Any
from pathlib import Path


def load_txt(file_path: str) -> List[Dict[str, Any]]:
    """
    Load a .txt file, splitting on double newlines into virtual pages.
    """
    path = Path(file_path)
    pages = []

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        sections = [s.strip() for s in content.split("\n\n") if s.strip()]

        for i, section in enumerate(sections, start=1):
            pages.append({
                "page_number": i,
                "text": section,
                "section_heading": f"Section {i}",
                "source": path.name,
                "file_path": str(path),
                "file_type": "txt",
            })

    except Exception as e:
        raise ValueError(f"Failed to load TXT '{file_path}': {e}")

    return pages


def load_markdown(file_path: str) -> List[Dict[str, Any]]:
    """Load a Markdown file, treating ## headings as section boundaries."""
    path = Path(file_path)
    pages = []

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.split("\n")
        current_heading = "Overview"
        current_lines = []
        page_num = 1

        for line in lines:
            if line.startswith("## "):
                if current_lines:
                    pages.append({
                        "page_number": page_num,
                        "text": "\n".join(current_lines).strip(),
                        "section_heading": current_heading,
                        "source": path.name,
                        "file_path": str(path),
                        "file_type": "md",
                    })
                    page_num += 1
                    current_lines = []
                current_heading = line.lstrip("# ").strip()
            else:
                current_lines.append(line)

        if current_lines:
            pages.append({
                "page_number": page_num,
                "text": "\n".join(current_lines).strip(),
                "section_heading": current_heading,
                "source": path.name,
                "file_path": str(path),
                "file_type": "md",
            })

    except Exception as e:
        raise ValueError(f"Failed to load Markdown '{file_path}': {e}")

    return pages
