"""
Módulo de chunking semântico avançado.

Estratégias implementadas:
1. Semantic Chunking - Respeita limites de sentenças e parágrafos
2. Metadata Enrichment - Adiciona contexto estrutural aos chunks
3. Adaptive Overlap - Overlap inteligente baseado no conteúdo
4. Sentence-aware Boundaries - Não quebra sentenças no meio
"""

import re
from typing import List, Dict
import nltk
from nltk.tokenize import sent_tokenize

# Download necessário (apenas primeira vez)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)


def split_into_sentences(text: str) -> List[str]:
    """
    Divide texto em sentenças usando NLTK (mais preciso que regex).
    Lida bem com abreviações e pontuação complexa.
    """
    try:
        sentences = sent_tokenize(text, language='portuguese')
        return [s.strip() for s in sentences if s.strip()]
    except Exception:
        # Fallback para split simples se NLTK falhar
        return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]


def detect_paragraphs(text: str) -> List[str]:
    """
    Detecta parágrafos baseado em quebras de linha duplas.
    Parágrafos são unidades semânticas importantes.
    """
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]


def calculate_semantic_overlap(chunk_size: int) -> int:
    """
    Calcula overlap adaptativo baseado no tamanho do chunk.
    Chunks maiores precisam de mais overlap para contexto.
    """
    # 15-20% de overlap é ideal para manter contexto
    return max(150, int(chunk_size * 0.18))


def chunk_text_semantic(
    pages: List[str],
    target_chunk_size: int = 800,
    max_chunk_size: int = 1200,
    min_chunk_size: int = 200
) -> List[Dict]:
    """
    Chunking semântico avançado que respeita estrutura do texto.
    
    Melhorias sobre chunking básico:
    - Respeita limites de sentenças (não quebra no meio)
    - Respeita limites de parágrafos quando possível
    - Overlap adaptativo baseado em conteúdo
    - Metadata enriquecido (título de seção, contexto)
    - Chunks mais naturais e semanticamente coerentes
    
    Args:
        pages: Lista de textos (um por página)
        target_chunk_size: Tamanho ideal do chunk (mais flexível)
        max_chunk_size: Tamanho máximo permitido
        min_chunk_size: Tamanho mínimo permitido
    
    Returns:
        Lista de dicts com chunks e metadata enriquecido
    """
    chunks = []
    
    for page_num, page_text in enumerate(pages):
        if not page_text.strip():
            continue
        
        # Detecta possível título de seção (linhas curtas em maiúsculas ou negrito)
        section_title = extract_section_title(page_text)
        
        # Divide em parágrafos primeiro (preserva estrutura)
        paragraphs = detect_paragraphs(page_text)
        
        current_chunk = ""
        chunk_sentences = []
        
        for para in paragraphs:
            sentences = split_into_sentences(para)
            
            for sentence in sentences:
                # Verifica se adicionar esta sentença excede o tamanho máximo
                test_chunk = current_chunk + " " + sentence if current_chunk else sentence
                
                if len(test_chunk) <= max_chunk_size:
                    current_chunk = test_chunk
                    chunk_sentences.append(sentence)
                else:
                    # Chunk atual está completo
                    if len(current_chunk) >= min_chunk_size:
                        chunks.append({
                            "content": current_chunk.strip(),
                            "page_start": page_num + 1,
                            "page_end": page_num + 1,
                            "section_title": section_title,
                            "sentence_count": len(chunk_sentences),
                            "is_complete": True  # Não foi quebrado no meio
                        })
                        
                        # Overlap inteligente: mantém última sentença para contexto
                        if chunk_sentences:
                            overlap_size = calculate_semantic_overlap(len(current_chunk))
                            overlap_text = ""
                            
                            # Pega últimas sentenças até atingir overlap desejado
                            for s in reversed(chunk_sentences):
                                if len(overlap_text) + len(s) <= overlap_size:
                                    overlap_text = s + " " + overlap_text
                                else:
                                    break
                            
                            current_chunk = overlap_text.strip() + " " + sentence
                            chunk_sentences = [sentence]
                        else:
                            current_chunk = sentence
                            chunk_sentences = [sentence]
                    else:
                        # Chunk muito pequeno, continua acumulando
                        current_chunk = test_chunk
                        chunk_sentences.append(sentence)
        
        # Adiciona chunk final da página
        if current_chunk.strip() and len(current_chunk) >= min_chunk_size:
            chunks.append({
                "content": current_chunk.strip(),
                "page_start": page_num + 1,
                "page_end": page_num + 1,
                "section_title": section_title,
                "sentence_count": len(chunk_sentences),
                "is_complete": True
            })
    
    # Merge chunks muito pequenos adjacentes
    chunks = merge_small_chunks(chunks, min_chunk_size)
    
    # Enriquece com metadata adicional
    chunks = enrich_chunk_metadata(chunks)
    
    return chunks


def extract_section_title(text: str) -> str:
    """
    Tenta extrair título de seção do início do texto.
    Heurísticas: linhas curtas (<80 chars), maiúsculas, ou números de capítulo.
    """
    lines = text.strip().split('\n')
    if not lines:
        return ""
    
    first_line = lines[0].strip()
    
    # Heurística 1: Linha curta em maiúsculas
    if len(first_line) < 80 and first_line.isupper():
        return first_line
    
    # Heurística 2: Começa com número (capítulo/seção)
    if re.match(r'^(\d+\.|\d+\)|\d+\s)', first_line):
        return first_line
    
    # Heurística 3: Palavra única ou frase curta em negrito (detecção simples)
    if len(first_line.split()) <= 5 and len(first_line) < 50:
        return first_line
    
    return ""


def merge_small_chunks(chunks: List[Dict], min_size: int) -> List[Dict]:
    """
    Mescla chunks muito pequenos com adjacentes para evitar fragmentação.
    """
    if not chunks:
        return chunks
    
    merged = []
    i = 0
    
    while i < len(chunks):
        current = chunks[i]
        
        # Se chunk é muito pequeno e não é o último, tenta mesclar
        if len(current["content"]) < min_size and i + 1 < len(chunks):
            next_chunk = chunks[i + 1]
            
            # Mescla se estão na mesma página ou páginas adjacentes
            if abs(current["page_start"] - next_chunk["page_start"]) <= 1:
                merged_content = current["content"] + " " + next_chunk["content"]
                merged.append({
                    "content": merged_content,
                    "page_start": current["page_start"],
                    "page_end": next_chunk["page_end"],
                    "section_title": current["section_title"] or next_chunk["section_title"],
                    "sentence_count": current["sentence_count"] + next_chunk["sentence_count"],
                    "is_complete": True
                })
                i += 2  # Pula os dois chunks
                continue
        
        merged.append(current)
        i += 1
    
    return merged


def enrich_chunk_metadata(chunks: List[Dict]) -> List[Dict]:
    """
    Adiciona metadata enriquecido aos chunks para melhor retrieval.
    """
    for i, chunk in enumerate(chunks):
        # Adiciona posição relativa no documento
        chunk["chunk_index"] = i
        chunk["total_chunks"] = len(chunks)
        chunk["relative_position"] = i / len(chunks) if len(chunks) > 0 else 0
        
        # Calcula densidade de informação (palavras únicas / total de palavras)
        words = chunk["content"].lower().split()
        unique_words = set(words)
        chunk["word_count"] = len(words)
        chunk["unique_word_ratio"] = len(unique_words) / len(words) if words else 0
        
        # Detecta se contém números/dados (importante para contexto factual)
        chunk["contains_numbers"] = bool(re.search(r'\d+', chunk["content"]))
        
        # Detecta listas ou enumerações
        chunk["has_list"] = bool(re.search(r'(\n\s*[-•*]\s|\n\s*\d+[\.)]\s)', chunk["content"]))
    
    return chunks


def chunk_text_hybrid(
    pages: List[str],
    use_semantic: bool = True,
    **kwargs
) -> List[Dict]:
    """
    Função wrapper que escolhe estratégia de chunking.
    
    Args:
        pages: Lista de páginas
        use_semantic: Se True, usa chunking semântico avançado
        **kwargs: Parâmetros passados para função de chunking
    
    Returns:
        Lista de chunks com metadata
    """
    if use_semantic:
        return chunk_text_semantic(pages, **kwargs)
    else:
        # Fallback para chunking básico (compatibilidade)
        from .rag import chunk_text as chunk_text_basic
        return chunk_text_basic(pages, **kwargs)
