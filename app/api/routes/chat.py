"""
Chat routes: query and history.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.db.session import get_db
from app.db.models import ChatSession, ChatMessage, QueryLog
from app.api.schemas import ChatRequest, ChatResponse, ChatMessage as ChatMessageSchema
from app.api.core.security import get_current_user_payload
from app.rag.pipelines.query_pipeline import run_query_pipeline
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


def _get_or_create_session(session_id: str, user_id: int, db: Session) -> ChatSession:
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        session = ChatSession(session_id=session_id, user_id=user_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    else:
        session.last_active = datetime.now(timezone.utc)
        db.commit()
    return session


@router.post("/query", response_model=ChatResponse, summary="Ask a question about your documents")
def query(
    req: ChatRequest,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload),
):
    """
    Main RAG query endpoint.
    Applies RBAC filtering at the retrieval level.
    Returns answer + citations + latency.
    """
    user_role = payload.get("role", "employee")
    user_id = payload.get("user_id")

    # Run the full RAG pipeline
    result = run_query_pipeline(
        question=req.question,
        user_role=user_role,
        session_id=req.session_id,
        top_k=req.top_k,
    )

    # Persist to DB
    try:
        session = _get_or_create_session(req.session_id, user_id, db)

        # Save user message
        user_msg = ChatMessage(session_id=session.id, role="user", content=req.question)
        db.add(user_msg)

        # Save assistant message
        assistant_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=result["answer"],
            citations=result["citations"],
        )
        db.add(assistant_msg)

        # Query log for analytics
        log = QueryLog(
            user_id=user_id,
            session_id=req.session_id,
            question=req.question,
            answer=result["answer"],
            sources_found=result["sources_found"],
            has_answer=result["has_answer"],
            latency_ms=result["latency_ms"],
            user_role=user_role,
            llm_model="gpt-4.1-mini",
        )
        db.add(log)
        db.commit()
    except Exception as e:
        logger.error(f"DB persist error in /chat/query: {e}")
        # Don't fail the response — just log

    return ChatResponse(**result)


@router.get("/history/{session_id}", response_model=List[ChatMessageSchema],
            summary="Get chat history for a session")
def get_history(
    session_id: str,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload),
):
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")

    # Users can only access their own sessions
    user_id = payload.get("user_id")
    if payload.get("role") != "admin" and session.user_id != user_id:
        raise HTTPException(403, "Access denied")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.id.asc())
        .all()
    )
    return messages


@router.get("/sessions", summary="List chat sessions for the current user")
def list_sessions(
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user_payload),
):
    user_id = payload.get("user_id")
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).all()
    return [{"session_id": s.session_id, "created_at": s.created_at,
             "last_active": s.last_active} for s in sessions]
