"""
Tests for retrieval — embedding, ChromaDB operations, citations, groundedness.
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEmbedder:
    def test_embed_query_returns_vector(self):
        from app.rag.embeddings.embedder import EmbeddingService
        svc = EmbeddingService()
        vec = svc.embed_query("test query")
        assert isinstance(vec, list)
        assert len(vec) == 384  # all-MiniLM-L6-v2 output dim
        assert all(isinstance(v, float) for v in vec)

    def test_embed_batch(self):
        from app.rag.embeddings.embedder import EmbeddingService
        svc = EmbeddingService()
        vecs = svc.embed(["first text", "second text", "third text"])
        assert len(vecs) == 3
        assert all(len(v) == 384 for v in vecs)

    def test_embed_empty_returns_empty(self):
        from app.rag.embeddings.embedder import EmbeddingService
        svc = EmbeddingService()
        result = svc.embed([])
        assert result == []

    def test_singleton(self):
        from app.rag.embeddings.embedder import EmbeddingService
        s1 = EmbeddingService()
        s2 = EmbeddingService()
        assert s1 is s2


class TestCitations:
    def test_build_citations_basic(self):
        from app.rag.generation.citations import build_citations
        chunks = [
            {"text": "Policy text here...", "metadata": {
                "file_name": "HR_Policy.pdf", "page_number": 5,
                "section_heading": "Leave Policy", "department": "hr"
            }, "score": 0.92},
        ]
        cits = build_citations(chunks)
        assert len(cits) == 1
        assert cits[0]["document"] == "HR_Policy.pdf"
        assert cits[0]["page"] == 5
        assert cits[0]["section"] == "Leave Policy"
        assert cits[0]["score"] == 0.92

    def test_build_citations_deduplication(self):
        from app.rag.generation.citations import build_citations
        chunks = [
            {"text": "Text A", "metadata": {"file_name": "doc.pdf", "page_number": 1, "section_heading": "", "department": "public"}, "score": 0.9},
            {"text": "Text B", "metadata": {"file_name": "doc.pdf", "page_number": 1, "section_heading": "", "department": "public"}, "score": 0.85},
        ]
        cits = build_citations(chunks)
        # Same doc+page = deduplicated
        assert len(cits) == 1

    def test_format_citation_text(self):
        from app.rag.generation.citations import format_citation_text
        cit = {"document": "Policy.pdf", "page": 12, "section": "4.2"}
        text = format_citation_text(cit)
        assert "Policy.pdf" in text
        assert "12" in text
        assert "4.2" in text


class TestGroundedness:
    def test_no_chunks_not_grounded(self):
        from app.rag.guardrails.hallucination_checks import is_grounded
        assert is_grounded("Some answer", []) is False

    def test_not_found_answer_is_grounded(self):
        from app.rag.guardrails.hallucination_checks import is_grounded
        chunks = [{"score": 0.5}]
        answer = "This information was not found in the indexed documents."
        assert is_grounded(answer, chunks) is True

    def test_filter_low_quality_chunks(self):
        from app.rag.guardrails.hallucination_checks import filter_low_quality_chunks
        chunks = [
            {"text": "good", "score": 0.8},
            {"text": "bad", "score": 0.1},
            {"text": "ok", "score": 0.5},
        ]
        filtered = filter_low_quality_chunks(chunks, min_score=0.3)
        assert len(filtered) == 2
        assert all(c["score"] >= 0.3 for c in filtered)


class TestPromptBuilder:
    def test_prompt_contains_question(self):
        from app.rag.generation.prompt_builder import build_prompt
        chunks = [{"text": "Some context here.", "metadata": {
            "file_name": "doc.pdf", "page_number": 1, "section_heading": ""
        }}]
        prompt = build_prompt("What is the policy?", chunks)
        assert "What is the policy?" in prompt
        assert "Some context here." in prompt

    def test_prompt_contains_source_labels(self):
        from app.rag.generation.prompt_builder import build_prompt
        chunks = [{"text": "Content", "metadata": {
            "file_name": "HR.pdf", "page_number": 3, "section_heading": "Leave"
        }}]
        prompt = build_prompt("Question?", chunks)
        assert "HR.pdf" in prompt
        assert "Page 3" in prompt

    def test_prompt_injection_defense_in_template(self):
        from app.rag.generation.prompt_builder import RAG_PROMPT_TEMPLATE
        assert "untrusted" in RAG_PROMPT_TEMPLATE.lower()
