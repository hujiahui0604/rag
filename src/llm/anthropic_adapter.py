"""Anthropic Claude LLM adapter"""
from typing import Optional

from ..config import ANTHROPIC_API_KEY


class AnthropicLLM:
    """Anthropic Claude LLM wrapper for RAG"""

    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.model = model
        self.api_key = ANTHROPIC_API_KEY

    def generate_answer(self, question: str, context: str) -> str:
        """Generate answer using Anthropic Claude with RAG context"""
        if not self.api_key:
            return "Error: ANTHROPIC_API_KEY not set in environment or .env file"

        try:
            from anthropic import Anthropic
        except ImportError:
            return "Error: anthropic package not installed"

        client = Anthropic(api_key=self.api_key)

        prompt = f"""You are a helpful assistant answering questions based on the provided context.
If the answer is in the context, provide it. If not, say you don't have enough information.

Context:
{context}

Question: {question}

Answer:"""

        try:
            response = client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.7,
                system="You are a helpful assistant that answers questions based on the provided context.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error generating answer: {str(e)}"