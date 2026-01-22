"""
Módulo RAG (Retrieval-Augmented Generation) - VERSÃO AVANÇADA.

FILOSOFIA FUNDAMENTAL DO SISTEMA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 REGRA DE OURO: Respostas APENAS baseadas no acervo de PDFs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. FONTES PERMITIDAS:
   ✅ Documentos PDF indexados no FAISS
   ✅ Contextos recuperados pela busca vetorial/híbrida
    ❌ Conhecimento prévio do LLM (Groq/LLM)
   ❌ Informações externas ou de bases de conhecimento gerais

2. PAPEL DO LLM (GROQ - LLAMA 3.x):
    - ÚNICO uso: Reformular linguisticamente os contextos recuperados
    - PROIBIDO: Adicionar informações, deduzir, supor, inventar
    - LLM = "Tradutor de contextos para linguagem natural"

3. QUANDO NÃO HÁ INFORMAÇÃO:
   - Retornar "Não encontrei essa informação no acervo"
   - NUNCA tentar responder com conhecimento geral
   - NUNCA completar informações parciais

4. MELHORIAS TÉCNICAS (SEMPRE RESPEITANDO REGRA DE OURO):
   - Chunking semântico: Melhora qualidade dos contextos extraídos
   - Hybrid Search: Melhora recall (encontra mais contextos relevantes)
   - Query Expansion: Reformula pergunta para buscar melhor
   - Re-ranking: Ordena contextos por relevância
   - Prompt Engineering: Instrui Gemini a NÃO inventar

Responsável por:
  - Extrair texto de PDFs
  - Chunking semântico inteligente (respeita sentenças e parágrafos)
  - Criar e gerenciar índice FAISS
  - Hybrid Search (Dense FAISS + Sparse BM25)
  - Query Expansion (sinônimos + LLM reformulation)
  - Buscar documentos relevantes com re-ranking
  - Gerar respostas SOMENTE a partir dos contextos recuperados
  - Cache de respostas frequentes
"""

import json
import os
import uuid
import time
from pathlib import Path
from typing import Optional, List, Dict

import numpy as np
import fitz  # PyMuPDF
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI, APIError, RateLimitError
from . import settings
from .cache import get_response_cache
from .reranker import rerank_results
from .chunking import chunk_text_semantic, chunk_text_hybrid
from .hybrid_search import HybridSearch, create_hybrid_searcher
from .query_expansion import get_query_expander


# Cache global para o embedder (evita recarregar múltiplas vezes)
_embedder: Optional[SentenceTransformer] = None

# Cache global para hybrid searcher
_hybrid_searcher: Optional[HybridSearch] = None


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
    
    # Cria chunks usando chunking semântico avançado
    chunks = chunk_text_semantic(
        pages,
        target_chunk_size=800,  # Chunks menores e mais focados
        max_chunk_size=1200,
        min_chunk_size=200
    )
    print(f"  → {len(chunks)} chunks semânticos criados")
    
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
        
        # Salva chunk em metadados (com metadata enriquecido)
        chunk_metadata = {
            "document_id": doc_id,
            "chunk_id": chunk_id,
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "content": chunk["content"],
            # Metadata adicional do chunking semântico
            "section_title": chunk.get("section_title", ""),
            "sentence_count": chunk.get("sentence_count", 0),
            "word_count": chunk.get("word_count", 0),
            "is_complete": chunk.get("is_complete", True)
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
    embedder: Optional[SentenceTransformer] = None,
    use_reranking: bool = True,
    use_hybrid: bool = True,
    use_query_expansion: bool = True
) -> list[dict]:
    """
    Busca chunks relevantes com técnicas avançadas de RAG.
    
    Melhorias implementadas:
    - Query Expansion: Expande query com sinônimos e LLM
    - Hybrid Search: Combina FAISS (dense) + BM25 (sparse)
    - Re-ranking: Multi-signal scoring para melhor relevância
    
    Args:
        query: Pergunta do usuário
        top_k: Número de resultados a retornar
        min_sim: Similaridade mínima (0-1)
        index_dir: Diretório do índice FAISS
        embedder: Modelo de embedding (opcional)
        use_reranking: Se True, aplica re-ranking multi-signal
        use_hybrid: Se True, usa hybrid search (BM25 + Dense)
        use_query_expansion: Se True, expande query com sinônimos/LLM
    
    Returns:
        Lista de dicts com contextos relevantes ordenados por relevância
    """
    global _hybrid_searcher
    
    embedder = embedder or load_embedder()
    
    # Carrega índice e metadados
    faiss_index, metadata = load_or_create_index(index_dir)
    
    if faiss_index.ntotal == 0:
        return []
    
    chunks_metadata = metadata.get("chunks", [])
    docs_metadata = {doc["document_id"]: doc for doc in metadata.get("documents", [])}
    
    # === ETAPA 1: Query Expansion ===
    queries_to_search = [query]
    if use_query_expansion:
        expander = get_query_expander()
        queries_to_search = expander.expand(query)
        print(f"🔄 Query Expansion: 1 query → {len(queries_to_search)} queries")
    
    # === ETAPA 2: Dense Search (FAISS) para cada query ===
    all_results = {}  # dict para deduplicar por content
    
    for q in queries_to_search:
        # Embed a query
        query_embedding = embedder.encode(q, convert_to_numpy=True)
        query_embedding = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_embedding)
        
        # Busca no FAISS (pega mais resultados para filtrar depois)
        search_k = top_k * len(queries_to_search)  # Busca mais se tem expansão
        distances, indices = faiss_index.search(query_embedding, search_k)  # type: ignore
        distances = distances[0]
        indices = indices[0]
        
        # Processa resultados desta query
        for distance, idx in zip(distances, indices):
            if idx < 0 or idx >= len(chunks_metadata):
                continue
            
            score = float(distance)
            if score < min_sim:
                continue
            
            chunk_meta = chunks_metadata[idx]
            doc_id = chunk_meta["document_id"]
            doc_meta = docs_metadata.get(doc_id, {})
            
            content = chunk_meta["content"]
            
            # Deduplica: usa content como chave, mantém melhor score
            if content not in all_results or score > all_results[content]["score"]:
                all_results[content] = {
                    "content": content,
                    "title": doc_meta.get("title", "Unknown"),
                    "page_start": chunk_meta["page_start"],
                    "page_end": chunk_meta["page_end"],
                    "uri": doc_meta.get("source_uri", ""),
                    "score": score,
                    "matched_query": q  # Qual query expandida encontrou
                }
    
    results = list(all_results.values())
    print(f"🔍 Dense Search: {len(results)} resultados únicos (min_sim={min_sim})")
    
    if not results:
        return []
    
    # === ETAPA 3: Hybrid Search (BM25 + Dense) ===
    if use_hybrid:
        # Inicializa ou reutiliza hybrid searcher
        if _hybrid_searcher is None or len(_hybrid_searcher.corpus) != len(chunks_metadata):
            _hybrid_searcher = create_hybrid_searcher(chunks_metadata, alpha=0.65)
        
        results = _hybrid_searcher.search(query, results, top_k=top_k*2)
        print(f"🔀 Hybrid Search: {len(results)} resultados após BM25 fusion")
    
    # === ETAPA 4: Re-ranking Multi-Signal ===
    if use_reranking and results:
        results = rerank_results(query, results)
        print(f"📊 Re-ranking: {len(results)} resultados re-ordenados")
    
    # Retorna top-k finais
    final_results = results[:top_k]
    print(f"✅ Retornando {len(final_results)} resultados finais")
    
    return final_results


def generate_answer(question: str, contexts: list[dict], conversation_history: list[dict] = None) -> str:
    """
    Gera uma resposta coerente e sintetizada usando Groq (endpoint OpenAI-compatible).
    
    Estratégia:
    1. Se não houver contextos, avisa que precisa consultar dirigente
    2. Se houver contextos, envia para o modelo sintetizar uma resposta
    3. Modelo gera resposta em português, bem estruturada
    4. Adiciona citações de fontes (documentos e páginas)
    5. Considera histórico de conversa para perguntas de seguimento
    
    Integração: Groq Llama 3.x via client OpenAI-compatible
    """
    if not contexts:
        return "Não encontrei essa informação no acervo, entre em contato com o administrador da plataforma."
    
    try:
        # Configura Groq com a API key
        if not settings.GROQ_API_KEY:
            return "⚠️ Erro: GROQ_API_KEY não configurada. Por favor, defina a variável de ambiente."

        client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL,
        )
        model_name = settings.GROQ_MODEL or "llama-3.1-70b-versatile"
        
        # Monta contexto para Gemini (combina todos os chunks com fontes)
        context_text = "CONTEXTOS RELEVANTES DO ACERVO:\n\n"
        sources = set()
        
        for i, ctx in enumerate(contexts, 1):
            title = ctx.get("title", "Desconhecido")
            page_start = ctx.get("page_start", "?")
            page_end = ctx.get("page_end", "?")
            content = ctx.get("content", "").strip()
            score = ctx.get("final_score", ctx.get("score", 0))
            
            # Mantém estrutura interna mas não aparece na resposta ao usuário
            context_text += f"[DOCUMENTO] {title} (pp. {page_start}-{page_end}) | Relevância: {score:.2f}\n{content}\n\n"
            sources.add(f"{title} (pp. {page_start}-{page_end})")
        
        # Monta histórico de conversa se existir
        history_text = ""
        if conversation_history and len(conversation_history) > 0:
            history_text = "HISTÓRICO DA CONVERSA (para contexto):\n\n"
            for i, msg in enumerate(conversation_history[-3:], 1):  # Últimas 3 mensagens
                history_text += f"Pergunta {i}: {msg.get('question', '')}\n"
                history_text += f"Resposta {i}: {msg.get('answer', '')}\n\n"
            history_text += "---\n\n"
        
        # Prompt original (versão que funcionava bem) + proteção contra "Contexto X" + histórico
        prompt = f"""Com base nos documentos abaixo, responda a pergunta de forma clara e objetiva.

{history_text}DOCUMENTOS:
{context_text}

PERGUNTA ATUAL: {question}

INSTRUÇÕES IMPORTANTES:
- Responda em português, de forma educativa e respeitosa
- Use **negrito** para termos importantes
- Base sua resposta APENAS nas informações presentes nos documentos acima
- Se houver histórico de conversa, use-o para entender o contexto (ex: "aprofunde", "explique melhor", etc.)
- NÃO mencione "Contexto X", "Documento X" ou numeração na resposta ao usuário
- Se a informação não estiver nos documentos, responda: "Os documentos disponíveis tratam de [temas principais], mas não abordam especificamente [tema perguntado]."
- Seja claro, didático e fiel ao conteúdo dos documentos"""

        # Chama Groq com retry e exponential backoff
        max_retries = 3
        retry_delay = 2  # segundos
        answer = None

        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=800,
                )
                answer = response.choices[0].message.content.strip()
                break  # Sucesso, sai do loop
            except RateLimitError as e:
                # Erro 429 - Quota excedida
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    print(f"⚠️ Quota Groq excedida. Tentativa {attempt + 1}/{max_retries}. Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"✗ Quota Groq esgotada após {max_retries} tentativas")
                    return (
                        "🕐 **Limite de requisições atingido**\n\n"
                        "Nosso sistema utiliza o endpoint Groq (free tier).\n\n"
                        "**Por favor, aguarde 1 minuto e tente novamente.**\n\n"
                        "💡 *Dica: Perguntas já feitas recentemente são respondidas instantaneamente do cache.*"
                    )
            except APIError as e:
                print(f"✗ Erro de API Groq (tentativa {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return f"⚠️ Erro ao gerar resposta: {str(e)}"
            except Exception as e:
                print(f"✗ Erro ao chamar Groq (tentativa {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    return f"⚠️ Erro ao gerar resposta: {str(e)}"

        # Se não conseguiu resposta após retries
        if answer is None:
            return "Erro ao processar a pergunta. Por favor, tente novamente."
        
        # Validação básica
        if len(answer.strip()) < 15:
            print("⚠️ Resposta muito curta")
            return "Não encontrei essa informação no acervo, entre em contato com o administrador da plataforma."
        
        # Validação 3: Detecta frases que indicam conhecimento prévio (alucinação)
        hallucination_indicators = [
            "de acordo com a tradição",
            "na umbanda tradicional",
            "geralmente se diz que",
            "é sabido que",
            "segundo especialistas",
            "historicamente",
            "na prática comum",
            "tipicamente",
            "usualmente"
        ]
        
        answer_lower = answer.lower()
        for indicator in hallucination_indicators:
            if indicator in answer_lower:
                # Verifica se o indicador aparece nos contextos
                context_combined = " ".join([ctx.get("content", "").lower() for ctx in contexts])
                if indicator not in context_combined:
                    print(f"⚠️ ALERTA: Possível alucinação detectada - frase '{indicator}' não está nos contextos")
                    # Não bloqueia, mas loga o alerta
        
        print(f"✅ Resposta gerada ({len(answer)} caracteres)")

        # Retorna resposta do modelo (as fontes são exibidas pelo frontend)
        return answer

    except Exception as e:
        print(f"Erro ao chamar LLM: {e}")
        # Fallback: resposta simples se falhar
        return (
            f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}. "
            "Por favor, tente novamente mais tarde."
        )


def ask_with_cache(
    question: str,
    top_k: int = 8,
    min_sim: float = 0.30,
    use_cache: bool = True,
    use_reranking: bool = True,
    index_dir: str = None,
    conversation_history: list[dict] = None
) -> tuple[str, list[dict]]:
    """
    Função principal que integra cache, busca, re-ranking e geração de resposta.
    
    Args:
        question: Pergunta do usuário
        top_k: Número de documentos a recuperar
        min_sim: Similaridade mínima
        use_cache: Se True, usa cache de respostas
        use_reranking: Se True, aplica re-ranking
        index_dir: Diretório do índice (opcional, usa settings.INDEX_DIR se None)
        conversation_history: Histórico de perguntas/respostas anteriores
    
    Returns:
        Tupla (resposta, contextos)
    """
    if index_dir is None:
        index_dir = settings.INDEX_DIR
    
    cache = get_response_cache()
    
    # Tenta recuperar do cache
    if use_cache:
        cached = cache.get(question)
        if cached:
            return cached['answer'], cached['contexts']
    
    # Cache miss: busca + gera resposta
    contexts = search(
        query=question,
        top_k=top_k,
        min_sim=min_sim,
        index_dir=index_dir,
        use_reranking=use_reranking
    )
    
    answer = generate_answer(question, contexts, conversation_history=conversation_history)
    
    # Armazena no cache
    if use_cache:
        cache.set(question, answer, contexts)
    
    return answer, contexts
