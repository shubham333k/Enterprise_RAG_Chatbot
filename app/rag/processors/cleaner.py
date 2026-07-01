"""
Text cleaning utilities: normalize whitespace, remove junk characters.
"""
import re
from typing import List, Dict, Any


def clean_text(text: str) -> str:
    """
    Normalize text extracted from documents.
    - Remove excessive whitespace and blank lines
    - Remove non-printable characters
    - Normalize unicode dashes and quotes
    """
    if not text:
        return ""

    # Normalize unicode punctuation
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u00a0", " ")   # non-breaking space

    # Remove non-printable characters (except newlines/tabs)
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u00A1-\uFFFF]", " ", text)

    # Collapse multiple spaces
    text = re.sub(r" {2,}", " ", text)

    # Collapse more than 2 consecutive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove trailing spaces on each line
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    return text.strip()


def clean_pages(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply clean_text to the 'text' field of each page dict."""
    cleaned = []
    for page in pages:
        page = page.copy()
        page["text"] = clean_text(page.get("text", ""))
        if page["text"]:  # skip empty pages after cleaning
            cleaned.append(page)
    return cleaned
