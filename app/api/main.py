"""
FastAPI application entrypoint for Enterprise Knowledge Assistant.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.core.config import settings
from app.api.core.logging import logger
from app.api.core.security import get_current_user_payload
from app.api.routes import auth, documents, chat, analytics
from app.db.session import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.VERSION}")

    # Create DB tables on startup
    create_tables()
    logger.info("Database tables created/verified.")

    # Pre-warm the embedding model and vector store
    logger.info("Pre-warming embedding model...")
    from app.rag.embeddings.embedder import embedder  # triggers singleton load
    from app.rag.vectorstores.chroma_store import vector_store  # triggers singleton load
    logger.info(f"ChromaDB ready. Total chunks: {vector_store.count()}")

    yield  # App runs here

    logger.info("Shutting down.")


# ─── App Definition ────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "AI-Powered Multi-Document RAG Platform with Role-Based Access Control, "
        "Hybrid Semantic Search & Source Attribution. "
        "LLM runs in the cloud (OpenAI) — never locally."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(analytics.router)


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Health check endpoint")
def health():
    from app.rag.vectorstores.chroma_store import vector_store
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "vector_chunks": vector_store.count(),
        "llm_model": settings.OPENAI_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/health",
    }


# ─── Wire up /auth/me properly ─────────────────────────────────────────────────
@app.get("/auth/me", tags=["Authentication"], summary="Get current user info")
def me(payload: dict = Depends(get_current_user_payload)):
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
        "user_id": payload.get("user_id"),
    }
