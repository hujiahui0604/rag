"""Basic tests for RAG system"""
import pytest
from pathlib import Path
import tempfile
import os


def test_config_imports():
    """Test that config module imports correctly"""
    from src import config
    assert config.PROJECT_ROOT is not None


def test_ingest_loader():
    """Test document loader"""
    from src.ingest.loader import load_document
    # Test with a simple text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("This is a test document.")
        temp_path = f.name

    try:
        docs = load_document(temp_path)
        assert len(docs) > 0
        assert "test document" in docs[0].page_content.lower()
    finally:
        os.unlink(temp_path)


def test_text_splitter():
    """Test text splitter"""
    from src.ingest.splitter import split_text

    text = "This is a test. " * 100
    chunks = split_text(text, chunk_size=50, chunk_overlap=10)

    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)


def test_chroma_client_init():
    """Test Chroma client initialization"""
    from src.vectorstore.chroma_client import ChromaClient

    with tempfile.TemporaryDirectory() as tmpdir:
        # Temporarily override CHROMA_PATH
        from src import config
        original_path = config.CHROMA_PATH
        config.CHROMA_PATH = tmpdir

        client = ChromaClient()
        assert client.collection is not None
        assert client.get_count() == 0

        config.CHROMA_PATH = original_path