"""
Tests for text cleaning and chunking.
"""
import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ─── Cleaner Tests ────────────────────────────────────────────────────────────
class TestCleaner:
    def test_clean_basic_whitespace(self):
        from app.rag.processors.cleaner import clean_text
        result = clean_text("  Hello   world  ")
        assert "Hello" in result
        assert "world" in result

    def test_clean_unicode_quotes(self):
        from app.rag.processors.cleaner import clean_text
        result = clean_text("\u201cHello\u201d and \u2018world\u2019")
        assert '"Hello"' in result or '"Hello"' in result

    def test_clean_excessive_newlines(self):
        from app.rag.processors.cleaner import clean_text
        result = clean_text("Para 1\n\n\n\n\nPara 2")
        assert result.count("\n") <= 3  # max 2 consecutive newlines

    def test_clean_empty_string(self):
        from app.rag.processors.cleaner import clean_text
        assert clean_text("") == ""
        assert clean_text(None) == ""

    def test_clean_pages_filters_empty(self):
        from app.rag.processors.cleaner import clean_pages
        pages = [
            {"text": "Valid content here.", "page_number": 1},
            {"text": "   \n  ", "page_number": 2},  # should be filtered
            {"text": "More content.", "page_number": 3},
        ]
        result = clean_pages(pages)
        assert len(result) == 2


# ─── Chunker Tests ────────────────────────────────────────────────────────────
class TestChunker:
    def test_basic_chunking(self):
        from app.rag.processors.chunker import chunk_pages
        pages = [{"text": "This is a test paragraph. " * 100, "page_number": 1, "section_heading": "Test"}]
        chunks = chunk_pages(pages, document_id=1, file_name="test.txt",
                             department="public", access_level="public")
        assert len(chunks) > 0
        assert all("text" in c for c in chunks)
        assert all("metadata" in c for c in chunks)

    def test_metadata_preserved(self):
        from app.rag.processors.chunker import chunk_pages
        pages = [{"text": "Hello world. " * 10, "page_number": 5, "section_heading": "Chapter 1"}]
        chunks = chunk_pages(pages, document_id=42, file_name="my_doc.pdf",
                             department="hr", access_level="hr")
        meta = chunks[0]["metadata"]
        assert meta["document_id"] == 42
        assert meta["file_name"] == "my_doc.pdf"
        assert meta["department"] == "hr"
        assert meta["access_level"] == "hr"
        assert meta["page_number"] == 5
        assert meta["section_heading"] == "Chapter 1"

    def test_chunk_index_increments(self):
        from app.rag.processors.chunker import chunk_pages
        long_text = "word " * 1000
        pages = [{"text": long_text, "page_number": 1}]
        chunks = chunk_pages(pages, document_id=1, file_name="test.txt",
                             department="public", access_level="public")
        indices = [c["metadata"]["chunk_index"] for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_empty_pages_returns_no_chunks(self):
        from app.rag.processors.chunker import chunk_pages
        pages = [{"text": "", "page_number": 1}]
        chunks = chunk_pages(pages, document_id=1, file_name="empty.txt",
                             department="public", access_level="public")
        assert len(chunks) == 0
