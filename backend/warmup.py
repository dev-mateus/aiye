"""
Warmup script to pre-load the embedding model during deployment.
This runs after build to avoid OOM errors on first query.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Pre-load the embedding model."""
    try:
        print("🔥 Pre-loading embedding model...")
        from backend.rag import load_embedder
        load_embedder()
        print("✓ Embedding model pre-loaded successfully")
    except Exception as e:
        print(f"✗ Error pre-loading embedding model: {e}")
        print("⚠️  Continuing anyway - model will load on first query")

if __name__ == "__main__":
    main()
