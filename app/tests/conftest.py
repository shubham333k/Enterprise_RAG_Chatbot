"""
pytest configuration and shared fixtures.
"""
import os
import sys
import pytest

# Ensure project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables before any imports
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key-not-real")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_enterprise_rag.db")
os.environ.setdefault("CHROMA_PERSIST_DIR", "./test_chroma_db")
os.environ.setdefault("DEBUG", "false")


@pytest.fixture(autouse=True, scope="session")
def cleanup_test_db():
    """Clean up test database files after the test session."""
    yield
    import glob
    for f in glob.glob("test_enterprise_rag.db"):
        try:
            os.remove(f)
        except Exception:
            pass
    import shutil
    if os.path.exists("./test_chroma_db"):
        try:
            shutil.rmtree("./test_chroma_db")
        except Exception:
            pass
