"""
Document management routes: upload, index, list.
"""
import os
import shutil
from pathlib import Path
from typing import List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Document
from app.api.schemas import DocumentIndexRequest, DocumentResponse
from app.api.core.config import settings
from app.api.core.security import get_current_user_payload, require_role
from app.rag.pipelines.ingest_pipeline import run_ingest_pipeline

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xls", ".csv", ".txt", ".md"}


@router.post("/upload", status_code=201, summary="Upload a document")
async def upload_document(
    file: UploadFile = File(...),
    department: str = Form(default="public"),
    access_level: str = Form(default="public"),
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload),
):
    """Upload a document file. Supported: PDF, DOCX, XLSX, CSV, TXT, MD."""
    path = Path(file.filename)
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {path.suffix}. "
                                 f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    # Size check
    content = await file.read()
    size_kb = len(content) // 1024
    if size_kb > settings.MAX_UPLOAD_SIZE_MB * 1024:
        raise HTTPException(400, f"File too large. Max: {settings.MAX_UPLOAD_SIZE_MB} MB")

    # Save to disk
    save_dir = Path(settings.UPLOAD_DIR) / department
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / file.filename

    with open(save_path, "wb") as f:
        f.write(content)

    # Record in DB
    doc = Document(
        file_name=file.filename,
        file_type=path.suffix.lstrip(".").lower(),
        file_path=str(save_path),
        department=department,
        access_level=access_level,
        status="uploaded",
        file_size_kb=size_kb,
        uploaded_by=payload.get("user_id"),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {"document_id": doc.id, "file_name": doc.file_name, "status": "uploaded",
            "message": "File uploaded. Call /documents/index to index it."}


@router.post("/index", summary="Chunk, embed, and index a document")
def index_document(
    req: DocumentIndexRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["admin", "hr", "engineering", "sales"])),
):
    """Trigger the full RAG ingestion pipeline for an uploaded document."""
    doc = db.query(Document).filter(Document.id == req.document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    if doc.status == "indexed":
        return {"message": "Document already indexed", "chunk_count": doc.chunk_count}

    # Override access level if provided in request
    if req.access_level:
        doc.access_level = req.access_level
    if req.department:
        doc.department = req.department

    result = run_ingest_pipeline(
        file_path=doc.file_path,
        document_id=doc.id,
        file_name=doc.file_name,
        department=doc.department,
        access_level=doc.access_level,
    )

    if result["success"]:
        doc.status = "indexed"
        doc.chunk_count = result["chunk_count"]
        doc.indexed_at = datetime.now(timezone.utc)
    else:
        doc.status = "failed"
    db.commit()

    if not result["success"]:
        raise HTTPException(500, f"Indexing failed: {result['error']}")

    return {
        "document_id": doc.id,
        "file_name": doc.file_name,
        "status": "indexed",
        "chunk_count": result["chunk_count"],
    }


@router.get("", response_model=List[DocumentResponse], summary="List all documents")
def list_documents(
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload),
):
    """List all uploaded documents. Admins see all; others see public + their department."""
    role = payload.get("role", "employee")
    docs = db.query(Document).all()

    # Filter by access for non-admins
    if role != "admin":
        from app.rag.guardrails.access_control import get_allowed_access_levels
        allowed = get_allowed_access_levels(role)
        docs = [d for d in docs if d.access_level in allowed]

    return docs


@router.delete("/{document_id}", summary="Delete a document and its vector embeddings")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["admin"])),
):
    """Admin-only: delete document and remove its chunks from ChromaDB."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    from app.rag.vectorstores.chroma_store import vector_store
    deleted_chunks = vector_store.delete_by_document_id(document_id)

    # Remove file from disk
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception:
        pass

    db.delete(doc)
    db.commit()

    return {"message": f"Deleted document '{doc.file_name}' and {deleted_chunks} vector chunks."}
