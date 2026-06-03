"""OpenAI LLM adapter"""
from typing import Optional

from ..config import OPENAI_API_KEY


class OpenAILLM:
    """OpenAI LLM wrapper for RAG"""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = OPENAI_API_KEY

    def generate_answer(self, question: str, context: str) -> str:
        """Generate answer using OpenAI with RAG context"""
        try:
            from openai import OpenAI
        except ImportError:
            return "Error: openai package not installed"

        client = OpenAI(api_key=self.api_key)

        prompt = f"""You are a helpful assistant answering questions based on the provided context.
If the answer is in the context, provide it. If not, say you don't have enough information.

Context:
{context}

Question: {question}

Answer:"""

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating answer: {str(e)}"