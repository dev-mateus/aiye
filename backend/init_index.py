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
    try:
        from backend import settings
    except Exception as e:
        print(f"⚠️ Erro ao importar settings: {e}")
        print("Usando paths padrão...")
        # Fallback para paths padrão
        class FallbackSettings:
            INDEX_DIR = "backend/data/index"
            PDF_DIR = "backend/data/pdfs"
        settings = FallbackSettings()
    
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
    try:
        from backend.ingest import ingest_all_pdfs
        ingest_all_pdfs()
        print("✅ Índice inicializado com sucesso!")
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("⚠️ Pulando inicialização (será feito no primeiro warmup)")
        # Não falha o build, apenas avisa
        return
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        import traceback
        traceback.print_exc()
        # Não falha o build se já existir índice válido
        if index_path.exists() and metadata_path.exists():
            print("⚠️ Usando índice existente")
            return
        sys.exit(1)

if __name__ == "__main__":
    init_index()
