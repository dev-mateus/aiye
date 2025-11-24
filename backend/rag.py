"""
Módulo RAG (Retrieval-Augmented Generation).
Responsável por:
  - Extrair texto de PDFs
  - Chunk de texto com overlap
  - Criar e gerenciar índice FAISS
  - Buscar documentos relevantes
  - Gerar respostas a partir dos contextos recuperados
"""

import json
import os
import uuid
from pathlib import Path
from typing import Optional

import numpy as np
import fitz  # PyMuPDF
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from . import settings


# Cache global para o embedder (evita recarregar múltiplas vezes)
_embedder: Optional[SentenceTransformer] = None


def load_embedder() -> SentenceTransformer:
    """
    Carrega o modelo de embedding do HuggingFace.
    Utiliza cache global para evitar recarregamento.
    """
    global _embedder
    if _embedder is None:
        print(f"Carregando modelo de embedding: {settings.EMBEDDING_MODEL}")
        _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedder


def extract_text_from_pdf(pdf_path: str) -> list[str]:
    """
    Extrai texto de um PDF usando PyMuPDF (fitz).
    Retorna lista de strings, uma para cada página.
    """
    pages_text = []
    try:
        pdf_document = fitz.open(pdf_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text = page.get_text("text")
            pages_text.append(text)
        pdf_document.close()
        print(f"✓ Extraído texto de {len(pages_text)} páginas: {pdf_path}")
    except Exception as e:
        print(f"✗ Erro ao extrair texto de {pdf_path}: {e}")
    return pages_text


def chunk_text(
    pages: list[str],
    chunk_size: int = 1500,
    overlap: int = 200
) -> list[dict]:
    """
    Divide o texto em chunks com overlap.
    Cada chunk mantém referência à página inicial e final.
    
    Retorna lista de dicts: {"content": str, "page_start": int, "page_end": int}
    """
    chunks = []
    
    # Combina todas as páginas em um único texto, mas mantém track de páginas
    full_text = ""
    page_ranges = []  # Tuples (char_start, char_end, page_num)
    char_count = 0
    
    for page_num, page_text in enumerate(pages):
        start = char_count
        full_text += page_text + "\n\n"
        char_count = len(full_text)
        end = char_count
        page_ranges.append((start, end, page_num))
    
    # Cria chunks com overlap
    position = 0
    while position < len(full_text):
        chunk_end = min(position + chunk_size, len(full_text))
        chunk_content = full_text[position:chunk_end].strip()
        
        if chunk_content:
            # Determina página inicial e final
            page_start = 0
            page_end = len(pages) - 1
            for start, end, page_num in page_ranges:
                if start <= position < end:
                    page_start = page_num
                if start <= chunk_end - 1 < end:
                    page_end = page_num
            
            chunks.append({
                "content": chunk_content,
                "page_start": page_start + 1,  # 1-indexed
                "page_end": page_end + 1,
            })
        
        position += chunk_size - overlap
    
    return chunks


def load_or_create_index(index_dir: str) -> tuple[faiss.IndexFlatIP, dict]:
    """
    Carrega índice FAISS existente ou cria um novo.
    Também carrega metadados do JSON.
    
    Retorna: (faiss_index, metadata_dict)
    """
    index_path = os.path.join(index_dir, "index.faiss")
    metadata_path = os.path.join(index_dir, "metadata.json")
    
    # Carrega metadados
    metadata = {"documents": [], "chunks": []}
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            print(f"✓ Metadados carregados: {len(metadata.get('documents', []))} docs, {len(metadata.get('chunks', []))} chunks")
        except Exception as e:
            print(f"✗ Erro ao carregar metadados: {e}")
    
    # Carrega ou cria índice FAISS
    if os.path.exists(index_path):
        try:
            faiss_index = faiss.read_index(index_path)
            print(f"✓ Índice FAISS carregado: {faiss_index.ntotal} vetores")
        except Exception as e:
            print(f"✗ Erro ao carregar índice FAISS: {e}")
            faiss_index = faiss.IndexFlatIP(384)  # all-MiniLM-L6-v2 tem 384 dimensões
    else:
        # Cria novo índice
        faiss_index = faiss.IndexFlatIP(384)  # all-MiniLM-L6-v2 tem 384 dimensões
        print("✓ Novo índice FAISS criado (384 dimensões)")
    
    return faiss_index, metadata


def save_index_and_metadata(
    faiss_index: faiss.IndexFlatIP,
    metadata: dict,
    index_dir: str
) -> None:
    """Salva o índice FAISS e os metadados em disco."""
    os.makedirs(index_dir, exist_ok=True)
    
    # Salva índice FAISS
    index_path = os.path.join(index_dir, "index.faiss")
    faiss.write_index(faiss_index, index_path)
    print(f"✓ Índice FAISS salvo: {index_path}")
    
    # Salva metadados
    metadata_path = os.path.join(index_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"✓ Metadados salvos: {metadata_path}")


def add_document_to_index(
    pdf_path: str,
    title: str,
    index_dir: str = settings.INDEX_DIR,
    embedder: Optional[SentenceTransformer] = None
) -> None:
    """
    Extrai texto de um PDF, cria chunks, embed e adiciona ao índice FAISS.
    Atualiza os metadados em JSON.
    """
    embedder = embedder or load_embedder()
    
    # Extrai texto
    pages = extract_text_from_pdf(pdf_path)
    if not pages:
        return
    
    # Cria chunks
    chunks = chunk_text(pages)
    print(f"  → {len(chunks)} chunks criados")
    
    # Carrega índice e metadados
    faiss_index, metadata = load_or_create_index(index_dir)
    
    # Cria documento
    doc_id = str(uuid.uuid4())
    source_uri = pdf_path
    doc_metadata = {
        "document_id": doc_id,
        "title": title,
        "source_uri": source_uri,
        "pages": len(pages)
    }
    metadata["documents"].append(doc_metadata)
    
    # Processa chunks
    embeddings_list = []
    for chunk in chunks:
        chunk_id = str(uuid.uuid4())
        
        # Embed
        embedding = embedder.encode(chunk["content"], convert_to_numpy=True)
        embeddings_list.append(embedding)
        
        # Salva chunk em metadados
        chunk_metadata = {
            "document_id": doc_id,
            "chunk_id": chunk_id,
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "content": chunk["content"]
        }
        metadata["chunks"].append(chunk_metadata)
    
    # Adiciona embeddings ao índice
    if embeddings_list:
        embeddings_array = np.array(embeddings_list, dtype=np.float32)
        faiss.normalize_L2(embeddings_array)
        faiss_index.add(embeddings_array)  # type: ignore
        print(f"  → {len(embeddings_list)} embeddings adicionados ao índice")
    
    # Salva índice e metadados
    save_index_and_metadata(faiss_index, metadata, index_dir)


def search(
    query: str,
    top_k: int = 8,
    min_sim: float = 0.30,
    index_dir: str = settings.INDEX_DIR,
    embedder: Optional[SentenceTransformer] = None
) -> list[dict]:
    """
    Busca chunks relevantes para a query no índice FAISS.
    
    Retorna lista de dicts com:
      - content: texto do chunk
      - title: título do documento
      - page_start, page_end: páginas
      - uri: caminho do PDF
      - score: similarity score
    """
    embedder = embedder or load_embedder()
    
    # Carrega índice e metadados
    faiss_index, metadata = load_or_create_index(index_dir)
    
    if faiss_index.ntotal == 0:
        return []
    
    # Embed a query
    query_embedding = embedder.encode(query, convert_to_numpy=True)
    query_embedding = np.array([query_embedding], dtype=np.float32)
    faiss.normalize_L2(query_embedding)
    
    # Busca no FAISS
    distances, indices = faiss_index.search(query_embedding, int(top_k))  # type: ignore
    distances = distances[0]
    indices = indices[0]
    
    print(f"🔍 Busca: '{query}' | Top-{top_k} | min_sim={min_sim}")
    print(f"   Scores retornados: {distances.tolist()}")
    print(f"   Índices retornados: {indices.tolist()}")
    print(f"   Total de chunks em metadata: {len(chunks_metadata)}")
    
    # Constrói resultados
    results = []
    chunks_metadata = metadata.get("chunks", [])
    docs_metadata = {doc["document_id"]: doc for doc in metadata.get("documents", [])}
    
    print(f"   Iniciando loop com {len(list(zip(distances, indices)))} items")
    
    for i, (distance, idx) in enumerate(zip(distances, indices)):
        print(f"   Loop {i}: idx={idx}, distance={distance}")
        
        if idx < 0 or idx >= len(chunks_metadata):
            print(f"   ❌ Índice {idx} fora do range (total chunks: {len(chunks_metadata)})")
            continue
        
        # Similarity score (FAISS IndexFlatIP retorna produto interno normalizado)
        score = float(distance)
        
        print(f"   Chunk {idx}: score={score:.4f} (min={min_sim})")
        
        if score < min_sim:
            print(f"   ❌ Filtrado por score baixo")
            continue
        
        chunk_meta = chunks_metadata[idx]
        doc_id = chunk_meta["document_id"]
        doc_meta = docs_metadata.get(doc_id, {})
        
        result = {
            "content": chunk_meta["content"],
            "title": doc_meta.get("title", "Unknown"),
            "page_start": chunk_meta["page_start"],
            "page_end": chunk_meta["page_end"],
            "uri": doc_meta.get("source_uri", ""),
            "score": score
        }
        results.append(result)
        print(f"   ✅ Adicionado: {doc_meta.get('title', 'Unknown')[:40]}... (pág {chunk_meta['page_start']})")
    
    print(f"   📊 Total de resultados retornados: {len(results)}")
    return results


def generate_answer(question: str, contexts: list[dict]) -> str:
    """
    Gera uma resposta coerente e sintetizada usando Google Gemini.
    
    Estratégia:
    1. Se não houver contextos, avisa que precisa consultar dirigente
    2. Se houver contextos, envia para Gemini sintetizar uma resposta
    3. Gemini gera resposta em português, bem estruturada
    4. Adiciona citações de fontes (documentos e páginas)
    
    Integração: Google Generative AI (Gemini) - modelo de ponta para português
    """
    if not contexts:
        return "Não encontrei essa informação no acervo, entre em contato com o administrador da plataforma."
    
    try:
        # Configura Gemini com a API key
        if not settings.GOOGLE_API_KEY:
            return "⚠️ Erro: GOOGLE_API_KEY não configurada. Por favor, defina a variável de ambiente."
        
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Monta contexto para Gemini (combina todos os chunks com fontes)
        context_text = "CONTEXTOS DO ACERVO DE UMBANDA:\n\n"
        sources = set()
        
        for ctx in contexts:
            title = ctx.get("title", "Desconhecido")
            page_start = ctx.get("page_start", "?")
            page_end = ctx.get("page_end", "?")
            content = ctx.get("content", "").strip()
            
            context_text += f"[{title} - pp. {page_start}-{page_end}]\n{content}\n\n"
            sources.add(f"{title} (pp. {page_start}-{page_end})")
        
        # Prompt bem estruturado em português
        prompt = f"""Você é um assistente especializado em conhecimentos sobre Umbanda.
Sua tarefa é responder a pergunta do usuário sintetizando os contextos fornecidos.

REGRAS IMPORTANTES:
1. Responda APENAS com base nos contextos fornecidos
2. Se o contexto for muito vago ou não contiver informação relevante, responda com exatamente: "NÃO_ENCONTREI"
3. Respeite as variações das tradições entre terreiros
4. Sempre mencione que consultar um dirigente é importante
5. Use português claro e acessível
6. Crie uma única resposta coerente (não liste trechos)
7. Cite os documentos de origem ao final

PERGUNTA: {question}

{context_text}

Gere uma resposta completa, sintetizada e bem estruturada em português:"""
        
        # Chama Gemini
        response = model.generate_content(prompt)
        answer = response.text.strip()
        # Se Gemini indicou que não encontrou, retorna a mensagem padrão
        if "NÃO_ENCONTREI" in answer.upper():
            return "Não encontrei essa informação no acervo, entre em contato com o administrador da plataforma."
        # Adiciona rodapé com fontes e aviso ético normalmente
        sources_text = "\n\n📚 **Fontes consultadas:**\n" + "\n".join(f"• {s}" for s in sorted(sources))
        ethical_warning = (
            "\n\n⚠️ **Aviso importante**: "
            "As tradições da Umbanda variam significativamente entre terreiros e regiões. "
            "Esta resposta é informativa baseada no acervo disponível e não substitui a orientação direta de um dirigente, "
            "mãe ou pai de santo. Sempre consulte sua comunidade espiritual para decisões práticas."
        )
        return answer + sources_text + ethical_warning
        
    except Exception as e:
        print(f"Erro ao chamar Gemini: {e}")
        # Fallback: resposta simples se falhar
        return (
            f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}. "
            "Por favor, consulte um dirigente ou tente novamente mais tarde."
        )
