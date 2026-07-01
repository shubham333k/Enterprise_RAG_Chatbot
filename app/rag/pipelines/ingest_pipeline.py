"""
Document ingestion pipeline.
Flow: File → Loader → Cleaner → Chunker → Embedder → ChromaDB
"""
import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

from app.rag.loaders.pdf_loader import load_pdf
from app.rag.loaders.docx_loader import load_docx
from app.rag.loaders.xlsx_loader import load_xlsx
from app.rag.loaders.txt_loader import load_txt, load_markdown
from app.rag.processors.cleaner import clean_pages
from app.rag.processors.chunker import chunk_pages
from app.rag.embeddings.embedder import embedder
from app.rag.vectorstores.chroma_store import vector_store
from app.api.core.config import settings

logger = logging.getLogger(__name__)

# Supported file extensions and their loaders
LOADER_MAP = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".xlsx": load_xlsx,
    ".xls": load_xlsx,
    ".csv": load_xlsx,
    ".txt": load_txt,
    ".md": load_markdown,
}


def run_ingest_pipeline(
    file_path: str,
    document_id: int,
    file_name: str,
    department: str = "public",
    access_level: str = "public",
    document_type: str = "document",
) -> dict:
    """
    Full ingestion pipeline for a single document.

    Args:
        file_path: Absolute path to the uploaded file.
        document_id: DB record ID for this document.
        file_name: Original filename (for metadata).
        department: Organizational department (hr/engineering/sales/public).
        access_level: Who can see this (public/hr/engineering/sales/legal).
        document_type: Document category label.

    Returns:
        {"success": bool, "chunk_count": int, "error": str|None}
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    logger.info(f"Starting ingestion: {file_name} (doc_id={document_id}, type={suffix})")

    # 1. Load
    loader = LOADER_MAP.get(suffix)
    if not loader:
        return {"success": False, "chunk_count": 0,
                "error": f"Unsupported file type: {suffix}"}

    try:
        pages = loader(file_path)
    except Exception as e:
        logger.error(f"Load failed for {file_name}: {e}")
        return {"success": False, "chunk_count": 0, "error": str(e)}

    if not pages:
        return {"success": False, "chunk_count": 0, "error": "No text extracted from document"}

    # 2. Clean
    pages = clean_pages(pages)

    # 3. Chunk
    chunks = chunk_pages(
        pages=pages,
        document_id=document_id,
        file_name=file_name,
        department=department,
        access_level=access_level,
        document_type=document_type,
        embedding_model=settings.EMBEDDING_MODEL,
    )

    if not chunks:
        return {"success": False, "chunk_count": 0, "error": "No chunks generated"}

    logger.info(f"Generated {len(chunks)} chunks for {file_name}")

    # 4. Embed
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    try:
        embeddings = embedder.embed(texts)
    except Exception as e:
        logger.error(f"Embedding failed for {file_name}: {e}")
        return {"success": False, "chunk_count": 0, "error": f"Embedding error: {e}"}

    # 5. Store in ChromaDB
    try:
        vector_store.add_chunks(
            texts=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )
    except Exception as e:
        logger.error(f"ChromaDB insert failed for {file_name}: {e}")
        return {"success": False, "chunk_count": 0, "error": f"Vector store error: {e}"}

    logger.info(f"Successfully indexed {len(chunks)} chunks for {file_name}")
    return {"success": True, "chunk_count": len(chunks), "error": None}
