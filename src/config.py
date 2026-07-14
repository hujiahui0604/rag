"""Configuration management for RAG system"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CHROMA_PATH = os.getenv("CHROMA_PATH", str(PROJECT_ROOT / "chroma_data"))
DATA_PATH = os.getenv("DATA_PATH", str(PROJECT_ROOT / "data" / "documents"))

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# LLM Provider selection
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai, anthropic, ollama