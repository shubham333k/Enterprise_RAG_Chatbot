"""
Tests for document loaders.
"""
import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path


def test_pdf_loader_imports():
    from app.rag.loaders.pdf_loader import load_pdf
    assert callable(load_pdf)


def test_docx_loader_imports():
    from app.rag.loaders.docx_loader import load_docx
    assert callable(load_docx)


def test_xlsx_loader_imports():
    from app.rag.loaders.xlsx_loader import load_xlsx
    assert callable(load_xlsx)


def test_txt_loader_basic():
    from app.rag.loaders.txt_loader import load_txt
    # Write a temp file
    test_path = "test_temp.txt"
    try:
        with open(test_path, "w") as f:
            f.write("Section one content here.\n\nSection two content here.\n\nSection three.")
        pages = load_txt(test_path)
        assert len(pages) == 3
        assert pages[0]["page_number"] == 1
        assert "Section one" in pages[0]["text"]
        assert pages[0]["file_type"] == "txt"
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)


def test_txt_loader_empty_sections():
    from app.rag.loaders.txt_loader import load_txt
    test_path = "test_empty.txt"
    try:
        with open(test_path, "w") as f:
            f.write("Only one section.")
        pages = load_txt(test_path)
        assert len(pages) == 1
        assert pages[0]["text"] == "Only one section."
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)


def test_txt_loader_metadata():
    from app.rag.loaders.txt_loader import load_txt
    test_path = "test_meta.txt"
    try:
        with open(test_path, "w") as f:
            f.write("Test content.")
        pages = load_txt(test_path)
        page = pages[0]
        assert "page_number" in page
        assert "text" in page
        assert "source" in page
        assert "file_path" in page
        assert "file_type" in page
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)


def test_markdown_loader():
    from app.rag.loaders.txt_loader import load_markdown
    test_path = "test_temp.md"
    try:
        with open(test_path, "w") as f:
            f.write("## Introduction\nThis is the intro.\n\n## Policy\nThis is the policy section.\n")
        pages = load_markdown(test_path)
        assert len(pages) >= 1
        assert any("Introduction" in p.get("section_heading", "") for p in pages)
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)
