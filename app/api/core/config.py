"""
Application configuration using Pydantic Settings.
Reads from environment variables / .env file.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "Enterprise Knowledge Assistant"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ── LLM Provider Selection ────────────────────────────────────────────────
    # Options: "openai" | "gemini" | "groq"
    LLM_PROVIDER: str = "gemini"

    # ── OpenAI (paid) ─────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = Field(default="sk-placeholder")
    OPENAI_MODEL: str = "gpt-4.1-mini"

    # ── Google Gemini (FREE — 1500 req/day) ───────────────────────────────────
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # ── Groq (FREE — very fast Llama 3) ──────────────────────────────────────
    GROQ_API_KEY: str = Field(default="")
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # ── Shared LLM settings ───────────────────────────────────────────────────
    LLM_MAX_TOKENS: int = 500
    LLM_TEMPERATURE: float = 0.2
    # Kept for backward compat
    OPENAI_MAX_TOKENS: int = 500
    OPENAI_TEMPERATURE: float = 0.2

    # ── Embeddings (local, ~90MB) ─────────────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── ChromaDB ──────────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    CHROMA_COLLECTION: str = "enterprise_docs"

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./data/enterprise_rag.db"

    # ── Auth ──────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── File Upload ───────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "./data/raw"
    MAX_UPLOAD_SIZE_MB: int = 50

    # ── RAG ───────────────────────────────────────────────────────────────────
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 125
    TOP_K_DEFAULT: int = 5

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 30

    # ── CORS ──────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8501", "http://localhost:3000", "*"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


# Singleton — import this everywhere
settings = Settings()

# Ensure directories exist at startup
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs("./data", exist_ok=True)
