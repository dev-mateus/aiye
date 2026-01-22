"""
Configurações globais do projeto.
Carrega variáveis de ambiente do arquivo .env na raiz do projeto.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env da raiz do projeto
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Backend
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
INDEX_DIR: str = os.getenv("INDEX_DIR", "backend/data/index")
PDF_DIR: str = os.getenv("PDF_DIR", "backend/data/pdfs")
METADATA_JSON: str = os.getenv("METADATA_JSON", "backend/data/index/metadata.json")
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
TOP_K: int = int(os.getenv("TOP_K", "8"))
MIN_SIM: float = float(os.getenv("MIN_SIM", "0.30"))
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

# Frontend
VITE_API_BASE: str = os.getenv("VITE_API_BASE", "http://localhost:8000")

# Garante que os diretórios existem
os.makedirs(INDEX_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
