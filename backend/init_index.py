"""
Script para inicializar o índice FAISS na primeira execução.
Roda automaticamente se o índice não existir.
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

def init_index():
    """Inicializa o índice FAISS se não existir."""
    from backend import settings
    from backend.rag import load_or_create_index
    
    index_path = Path(settings.INDEX_DIR) / "index.faiss"
    metadata_path = Path(settings.INDEX_DIR) / "metadata.json"
    
    # Verifica se AMBOS os arquivos existem
    if index_path.exists() and metadata_path.exists():
        print("✓ Índice e metadata já existem, pulando inicialização.")
        # Valida se metadata tem conteúdo
        import json
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                num_chunks = len(metadata.get("chunks", []))
                if num_chunks > 0:
                    print(f"✓ Metadata válido com {num_chunks} chunks")
                    return
                else:
                    print("⚠️ Metadata vazio, regenerando índice...")
        except Exception as e:
            print(f"⚠️ Erro ao ler metadata: {e}, regenerando índice...")
    
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    init_index()
