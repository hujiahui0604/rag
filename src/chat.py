"""Interactive chat interface for RAG"""
from .config import OPENAI_API_KEY
from .vectorstore.chroma_client import ChromaClient
from .retrieval.query_engine import QueryEngine


def main():
    """Start interactive chat session"""
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not set")
        return

    print("RAG Document Q&A Chat")
    print("Type 'quit' or 'exit' to end the session\n")

    chroma = ChromaClient()
    engine = QueryEngine(chroma)

    while True:
        try:
            query = input("You: ").strip()
            if query.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            if not query:
                continue

            result = engine.query(query)
            print(f"\nAssistant: {result['answer']}\n")
            if result.get("sources"):
                print("Sources:")
                for source in result["sources"]:
                    print(f"  - {source}")
                print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()