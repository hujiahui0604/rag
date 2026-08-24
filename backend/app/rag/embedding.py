"""Embedding service using Ollama"""
import asyncio
from functools import lru_cache
from typing import List, Optional
import httpx

from app.config import settings


# 全局查询缓存（已处理的 query 直接返回）
_query_cache: dict = {}
_CACHE_MAX_SIZE = 1000


class EmbeddingService:
    """Service for generating text embeddings using Ollama"""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.EMBEDDING_MODEL
        # 使用连接池，复用 TCP 连接
        self._sync_client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """懒加载同步客户端，使用连接池"""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                timeout=60.0,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10)
            )
        return self._sync_client

    def embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        """Generate embedding for a single text (synchronous).

        Args:
            text: The text to embed
            use_cache: Whether to use the query cache (default True)
        """
        # 查询缓存
        if use_cache and text in _query_cache:
            return _query_cache[text]

        try:
            response = self.client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text}
            )
            response.raise_for_status()
            data = response.json()
            embedding = self._normalize(data.get("embedding", []))

            # 添加到缓存
            if use_cache and embedding:
                if len(_query_cache) >= _CACHE_MAX_SIZE:
                    # 简单的 FIFO 淘汰策略
                    _query_cache.pop(next(iter(_query_cache)))
                _query_cache[text] = embedding

            return embedding
        except httpx.HTTPError as e:
            raise ConnectionError(f"Failed to get embedding from Ollama: {e}")
        except Exception as e:
            raise RuntimeError(f"Error generating embedding: {e}")

    def embed_texts(self, texts: List[str], max_concurrent: int = 10) -> List[List[float]]:
        """Generate embeddings for multiple texts using async batch processing."""
        if not texts:
            return []

        # 对于少量文本，直接用串行更稳定
        if len(texts) <= 3:
            return self._embed_texts_sync(texts)

        # 大量文本使用并发
        return asyncio.run(self._embed_texts_async(texts, max_concurrent))

    def _embed_texts_sync(self, texts: List[str]) -> List[List[float]]:
        """Synchronous embedding for small batch."""
        embeddings = []
        for text in texts:
            try:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
            except Exception as e:
                print(f"Warning: Failed to embed text: {e}")
                embeddings.append([])
        return embeddings

    async def _embed_texts_async(self, texts: List[str], max_concurrent: int = 10) -> List[List[float]]:
        """Async batch embedding with concurrency limit."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def embed_with_semaphore(text: str) -> List[float]:
            async with semaphore:
                return await self._embed_single_async(text)

        tasks = [embed_with_semaphore(text) for text in texts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        embeddings = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Warning: Failed to embed text: {result}")
                embeddings.append([])
            else:
                embeddings.append(result)

        return embeddings

    async def _embed_single_async(self, text: str) -> List[float]:
        """Async single embedding request."""
        async with httpx.AsyncClient(
            timeout=60.0,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10)
        ) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text}
                )
                response.raise_for_status()
                data = response.json()
                return self._normalize(data.get("embedding", []))
            except httpx.HTTPError as e:
                raise ConnectionError(f"Failed to get embedding from Ollama: {e}")
            except Exception as e:
                raise RuntimeError(f"Error generating embedding: {e}")

    @staticmethod
    def _normalize(vector: List[float]) -> List[float]:
        """L2-normalize an embedding vector to unit length."""
        norm = sum(v * v for v in vector) ** 0.5
        if not norm:
            return vector
        return [v / norm for v in vector]

    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding model."""
        try:
            embedding = self.embed_text("test", use_cache=False)
            return len(embedding)
        except Exception:
            return 768

    @staticmethod
    def get_cache_stats() -> dict:
        """Get cache statistics."""
        return {
            "size": len(_query_cache),
            "max_size": _CACHE_MAX_SIZE
        }

    @staticmethod
    def clear_cache() -> None:
        """Clear the query cache."""
        _query_cache.clear()

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