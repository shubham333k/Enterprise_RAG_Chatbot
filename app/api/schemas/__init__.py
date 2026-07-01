"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime


# ─── Auth ─────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[str] = None
    role: str = "employee"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


# ─── Documents ────────────────────────────────────────────────────────────────
class DocumentIndexRequest(BaseModel):
    document_id: int
    department: str = "public"
    access_level: str = "public"

class DocumentResponse(BaseModel):
    id: int
    file_name: str
    file_type: str
    department: str
    access_level: str
    status: str
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Chat ─────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str = "default"
    top_k: int = Field(default=5, ge=1, le=15)

class Citation(BaseModel):
    document: str
    page: Optional[int] = None
    section: Optional[str] = None
    excerpt: Optional[str] = None
    score: Optional[float] = None

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation] = []
    latency_ms: int
    session_id: str
    sources_found: int

class ChatMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Analytics ────────────────────────────────────────────────────────────────
class AnalyticsOverview(BaseModel):
    total_queries: int
    total_documents: int
    total_users: int
    avg_latency_ms: float
    no_answer_rate: float
    top_questions: List[dict]
    queries_by_role: dict
    recent_queries: List[dict]


# ─── Feedback ─────────────────────────────────────────────────────────────────
class FeedbackRequest(BaseModel):
    message_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
