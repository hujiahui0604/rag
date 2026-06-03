"""Main CLI entry point for RAG"""
import argparse
import sys
from pathlib import Path

from .config import DATA_PATH, OPENAI_API_KEY
from .ingest.loader import load_document
from .vectorstore.chroma_client import ChromaClient
from .retrieval.query_engine import QueryEngine


def main():
    parser = argparse.ArgumentParser(description="RAG Document Q&A System")
    parser.add_argument("--query", "-q", type=str, help="Query to ask the RAG system")
    parser.add_argument("--path", type=str, default=str(DATA_PATH), help="Path to documents")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild the index")
    args = parser.parse_args()

    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not set in environment or .env file")
        sys.exit(1)

    # Initialize components
    chroma = ChromaClient()
    engine = QueryEngine(chroma)

    # Rebuild index if requested
    if args.rebuild:
        print(f"Indexing documents from {args.path}...")
        _rebuild_index(chroma, args.path)
        print("Index rebuilt successfully!")

    # Process query
    if args.query:
        result = engine.query(args.query)
        print(f"\nQuestion: {args.query}")
        print(f"\nAnswer: {result['answer']}")
        if result.get("sources"):
            print("\nSources:")
            for source in result["sources"]:
                print(f"  - {source}")
    else:
        parser.print_help()


def _rebuild_index(chroma: ChromaClient, path: str):
    """Rebuild the Chroma index from documents"""
    from .ingest.splitter import split_documents

    documents = []
    metadata = []

    path_obj = Path(path)
    for file_path in path_obj.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in [".txt", ".md", ".pdf"]:
            try:
                docs = load_document(str(file_path))
                for doc in docs:
                    documents.append(doc.page_content)
                    metadata.append({
                        "source": str(file_path.name),
                        "path": str(file_path)
                    })
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")

    if documents:
        chroma.add_documents(documents, metadata)


if __name__ == "__main__":
    main()