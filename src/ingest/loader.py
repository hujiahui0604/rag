"""Document loaders for various file types"""
from pathlib import Path
from typing import List

try:
    from langchain_community.document_loaders import (
        TextLoader,
        MarkdownLoader,
        PyPDFLoader,
        UnstructuredMarkdownLoader
    )
except ImportError:
    from langchain.document_loaders import (
        TextLoader,
        MarkdownLoader,
        PyPDFLoader
    )

from langchain.schema import Document


def load_document(file_path: str) -> List[Document]:
    """Load a document from file path"""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        loader = PyPDFLoader(file_path)
    elif suffix == ".md":
        loader = MarkdownLoader(file_path)
    elif suffix == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return loader.load()


def load_directory(dir_path: str) -> List[Document]:
    """Load all supported documents from a directory"""
    documents = []
    path = Path(dir_path)

    for file_path in path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [".txt", ".md", ".pdf"]:
            try:
                docs = load_document(str(file_path))
                documents.extend(docs)
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")

    return documents