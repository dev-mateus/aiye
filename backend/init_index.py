"""
Script para inicializar o índice FAISS na primeira execução.
Roda automaticamente se o índice não existir.
"""
import os
from pathlib import Path
from backend.rag import load_or_create_index
from backend import settings

def init_index():
    """Inicializa o índice FAISS se não existir."""
    index_path = Path(settings.INDEX_DIR) / "index.faiss"
    
    if index_path.exists():
        print("✓ Índice já existe, pulando inicialização.")
        return
    
    print("🔨 Inicializando índice FAISS...")
    
    # Ingerir PDFs
    pdf_dir = Path(settings.PDF_DIR)
    if not pdf_dir.exists():
        print("❌ Diretório de PDFs não encontrado")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print("⚠️ Nenhum PDF encontrado em", settings.PDF_DIR)
        return
    
    print(f"Encontrados {len(pdf_files)} PDFs")
    
    # Roda o ingest
    from backend.ingest import ingest_all_pdfs
    try:
        ingest_all_pdfs()
        print("✅ Índice inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")

if __name__ == "__main__":
    init_index()
