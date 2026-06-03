"""Embedding service using Ollama"""
from typing import List
import httpx

from app.config import settings


class EmbeddingService:
    """Service for generating text embeddings using Ollama"""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.EMBEDDING_MODEL
        self.client = httpx.Client(timeout=60.0)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            response = self.client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])
        except httpx.HTTPError as e:
            raise ConnectionError(f"Failed to get embedding from Ollama: {e}")
        except Exception as e:
            raise RuntimeError(f"Error generating embedding: {e}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            try:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
            except Exception as e:
                print(f"Warning: Failed to embed text: {e}")
                embeddings.append([])
        return embeddings

    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding model."""
        try:
            embedding = self.embed_text("test")
            return len(embedding)
        except Exception:
            return 768

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MockEmbeddingService:
    """Mock embedding service for testing."""

    def __init__(self, dimension: int = 768):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Generate a mock embedding."""
        import hashlib
        hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [(hash_value >> i) % 2 for i in range(self.dimension)]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for multiple texts."""
        return [self.embed_text(text) for text in texts]

    def get_embedding_dimension(self) -> int:
        """Return the mock dimension."""
        return self.dimension

    def is_available(self) -> bool:
        """Always available."""
        return True