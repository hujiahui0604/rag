"""LLM service for generating responses using Ollama"""
from typing import List, Optional, Dict, Any
import httpx

from app.config import settings
from app.rag.vector_store import SearchResult


class LLMService:
    """Service for generating responses using Ollama"""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
        self.client = httpx.Client(timeout=120.0)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """Generate a response using Ollama."""
        full_prompt = self._build_prompt(prompt, system_prompt, context)

        try:
            response = self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except httpx.HTTPError as e:
            raise ConnectionError(f"Failed to get response from Ollama: {e}")
        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")

    def _build_prompt(
        self,
        user_prompt: str,
        system_prompt: Optional[str],
        context: Optional[str]
    ) -> str:
        """Build the full prompt with context."""
        parts = []

        if system_prompt:
            parts.append(f"System: {system_prompt}")

        if context:
            parts.append(
                f"Context information:\n{context}\n\n"
                "Based on the above context, please answer the following question. "
                "If the context doesn't provide enough information to answer, "
                "say so honestly.\n"
            )

        parts.append(f"User: {user_prompt}\n\nAssistant:")

        return "\n\n".join(parts)

    def generate_with_sources(
        self,
        query: str,
        sources: List[SearchResult],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a response with sources from retrieval."""
        context = self._build_context(sources)
        response = self.generate(query, system_prompt, context)

        return {
            "answer": response,
            "sources": [
                {
                    "text": source.text[:200] + "..." if len(source.text) > 200 else source.text,
                    "score": source.score,
                    "document_id": source.document_id
                }
                for source in sources
            ]
        }

    def _build_context(self, sources: List[SearchResult]) -> str:
        """Build context from retrieved sources."""
        if not sources:
            return ""

        context_parts = []
        for i, source in enumerate(sources, 1):
            context_parts.append(
                f"[Source {i}] (relevance: {source.score:.2f}):\n{source.text}"
            )

        return "\n\n".join(context_parts)

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return any(self.model in m.get("name", "") for m in models)
            return False
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            return []

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()