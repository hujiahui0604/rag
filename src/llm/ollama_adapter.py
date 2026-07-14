"""Ollama LLM adapter"""
from typing import Optional

from ..config import OLLAMA_BASE_URL, OLLAMA_MODEL


class OllamaLLM:
    """Ollama LLM wrapper for RAG"""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None
    ):
        self.model = model or OLLAMA_MODEL
        self.base_url = base_url or OLLAMA_BASE_URL

    def generate_answer(self, question: str, context: str) -> str:
        """Generate answer using Ollama with RAG context"""
        try:
            import requests
        except ImportError:
            return "Error: requests package not installed"

        prompt = f"""You are a helpful assistant answering questions based on the provided context.
If the answer is in the context, provide it. If not, say you don't have enough information.

Context:
{context}

Question: {question}

Answer:"""

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 1000
                    }
                },
                timeout=120
            )
            if response.status_code == 200:
                return response.json().get("response", "No response generated")
            else:
                return f"Error: Ollama API returned {response.status_code}"
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Is Ollama running?"
        except Exception as e:
            return f"Error generating answer: {str(e)}"