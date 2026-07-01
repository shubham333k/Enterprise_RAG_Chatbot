"""
Analytics routes — admin-only usage statistics.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.db.session import get_db
from app.db.models import QueryLog, Document, User, ChatMessage
from app.api.schemas import AnalyticsOverview
from app.api.core.security import require_role

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview, summary="Admin analytics dashboard")
def get_overview(
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["admin"])),
):
    """Returns usage statistics: query counts, latency, top questions, no-answer rate."""
    total_queries = db.query(func.count(QueryLog.id)).scalar() or 0
    total_documents = db.query(func.count(Document.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    avg_latency = db.query(func.avg(QueryLog.latency_ms)).scalar() or 0
    no_answer_count = db.query(func.count(QueryLog.id)).filter(
        QueryLog.has_answer == False
    ).scalar() or 0

    no_answer_rate = round(no_answer_count / max(total_queries, 1) * 100, 1)

    # Top questions (most common)
    top_q_rows = (
        db.query(QueryLog.question, func.count(QueryLog.id).label("count"))
        .group_by(QueryLog.question)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )
    top_questions = [{"question": r.question, "count": r.count} for r in top_q_rows]

    # Queries by role
    role_rows = (
        db.query(QueryLog.user_role, func.count(QueryLog.id).label("count"))
        .group_by(QueryLog.user_role)
        .all()
    )
    queries_by_role = {r.user_role or "unknown": r.count for r in role_rows}

    # Recent queries
    recent = (
        db.query(QueryLog)
        .order_by(desc(QueryLog.created_at))
        .limit(20)
        .all()
    )
    recent_queries = [
        {
            "question": r.question,
            "role": r.user_role,
            "latency_ms": r.latency_ms,
            "has_answer": r.has_answer,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recent
    ]

    return AnalyticsOverview(
        total_queries=total_queries,
        total_documents=total_documents,
        total_users=total_users,
        avg_latency_ms=round(avg_latency, 1),
        no_answer_rate=no_answer_rate,
        top_questions=top_questions,
        queries_by_role=queries_by_role,
        recent_queries=recent_queries,
    )


@router.get("/documents", summary="Document indexing status overview")
def get_document_stats(
    db: Session = Depends(get_db),
    payload: dict = Depends(require_role(["admin"])),
):
    """Returns document counts by status and access level."""
    from app.rag.vectorstores.chroma_store import vector_store
    status_rows = (
        db.query(Document.status, func.count(Document.id).label("count"))
        .group_by(Document.status).all()
    )
    access_rows = (
        db.query(Document.access_level, func.count(Document.id).label("count"))
        .group_by(Document.access_level).all()
    )
    return {
        "by_status": {r.status: r.count for r in status_rows},
        "by_access_level": {r.access_level: r.count for r in access_rows},
        "vector_chunks_total": vector_store.count(),
    }
