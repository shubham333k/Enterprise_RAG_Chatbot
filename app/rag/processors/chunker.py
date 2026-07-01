"""
Text chunking using LangChain's RecursiveCharacterTextSplitter.
Preserves metadata (page number, source, section) per chunk.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
from app.api.core.config import settings


def build_chunker() -> RecursiveCharacterTextSplitter:
    """
    Blueprint spec: 500–800 token chunks, 100–150 overlap.
    We use character count as a proxy (≈4 chars/token on average).
    CHUNK_SIZE=700 tokens ≈ 2800 chars; OVERLAP=125 tokens ≈ 500 chars.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE * 4,    # chars approximation
        chunk_overlap=settings.CHUNK_OVERLAP * 4,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
        is_separator_regex=False,
    )


def chunk_pages(
    pages: List[Dict[str, Any]],
    document_id: int,
    file_name: str,
    department: str,
    access_level: str,
    document_type: str = "document",
    embedding_model: str = "all-MiniLM-L6-v2",
) -> List[Dict[str, Any]]:
    """
    Split page dicts into chunks, attaching all required metadata.

    Returns:
        List of chunk dicts with 'text' and 'metadata' fields.
    """
    splitter = build_chunker()
    chunks = []
    chunk_index = 0

    for page in pages:
        text = page.get("text", "")
        if not text.strip():
            continue

        splits = splitter.split_text(text)
        for split_text in splits:
            if not split_text.strip():
                continue
            chunks.append({
                "text": split_text,
                "metadata": {
                    "document_id": document_id,
                    "file_name": file_name,
                    "department": department,
                    "document_type": document_type,
                    "page_number": page.get("page_number", 1),
                    "section_heading": page.get("section_heading", ""),
                    "access_level": access_level,
                    "chunk_index": chunk_index,
                    "source_path": page.get("file_path", ""),
                    "embedding_model": embedding_model,
                },
            })
            chunk_index += 1

    return chunks
