"""
Script de ingestão de PDFs.
Percorre o diretório PDF_DIR e adiciona cada PDF ao índice FAISS.
"""

import os
import sys
from pathlib import Path

# Support running the script either as a module (python -m backend.ingest)
# or directly (python backend/ingest.py) from the repository root.
try:
    from backend.rag import add_document_to_index, load_or_create_index
    from backend import settings
except ModuleNotFoundError:
    # When running `python backend/ingest.py` the package root may not be on sys.path.
    # Add the repository root (parent of this file's parent) to sys.path and retry.
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.append(str(repo_root))
    from backend.rag import add_document_to_index, load_or_create_index
    from backend import settings


def main():
    """
    Processa todos os PDFs em backend/data/pdfs/
    e cria/atualiza o índice FAISS em backend/data/index/
    """
    pdf_dir = settings.PDF_DIR
    index_dir = settings.INDEX_DIR
    
    # Valida diretórios
    if not os.path.exists(pdf_dir):
        print(f"✗ Diretório de PDFs não encontrado: {pdf_dir}")
        return
    
    os.makedirs(index_dir, exist_ok=True)
    
    # Lista PDFs
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith((".pdf", ".PDF"))]
    
    if not pdf_files:
        print(f"ℹ Nenhum arquivo PDF encontrado em: {pdf_dir}")
        print(f"  Por favor, coloque arquivos .pdf em {pdf_dir} e tente novamente.")
        return
    
    print(f"🔍 Encontrados {len(pdf_files)} arquivo(s) PDF:\n")
    
    # Processa cada PDF
    for pdf_filename in sorted(pdf_files):
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        print(f"📄 Processando: {pdf_filename}")
        
        # Usa o nome do arquivo (sem extensão) como título
        title = Path(pdf_filename).stem
        
        try:
            add_document_to_index(pdf_path, title, index_dir)
        except Exception as e:
            print(f"✗ Erro ao processar {pdf_filename}: {e}\n")
            continue
        
        print()
    
    # Exibe estatísticas finais
    _, metadata = load_or_create_index(index_dir)
    num_docs = len(metadata.get("documents", []))
    num_chunks = len(metadata.get("chunks", []))
    
    print("\n" + "="*60)
    print("✅ INGESTÃO CONCLUÍDA")
    print("="*60)
    print(f"  📚 Documentos: {num_docs}")
    print(f"  📦 Chunks: {num_chunks}")
    print(f"  📍 Índice: {os.path.join(index_dir, 'index.faiss')}")
    print(f"  📋 Metadados: {os.path.join(index_dir, 'metadata.json')}")
    print("\nAgora você pode iniciar o servidor FastAPI:")
    print("  uvicorn backend.main:app --reload --port 8000")
    print("="*60)


# Alias para compatibilidade
ingest_all_pdfs = main


if __name__ == "__main__":
    main()
