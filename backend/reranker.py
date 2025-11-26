"""
Sistema de re-ranking de documentos recuperados.
Melhora a relevância dos resultados usando múltiplos sinais.
"""

from typing import List, Dict
import re


def calculate_keyword_overlap(query: str, content: str) -> float:
    """
    Calcula sobreposição de palavras-chave entre query e conteúdo.
    
    Returns:
        Score entre 0 e 1 baseado na proporção de keywords presentes
    """
    # Extrai palavras significativas (remove stopwords comuns)
    stopwords = {
        'a', 'o', 'e', 'de', 'da', 'do', 'em', 'para', 'com', 'por', 'um', 'uma',
        'os', 'as', 'dos', 'das', 'que', 'é', 'no', 'na', 'são', 'se', 'foi',
        'como', 'qual', 'quais', 'quando', 'onde', 'porque', 'por que'
    }
    
    query_words = set(re.findall(r'\w+', query.lower()))
    query_words = query_words - stopwords
    
    if not query_words:
        return 0.0
    
    content_lower = content.lower()
    matches = sum(1 for word in query_words if word in content_lower)
    
    return matches / len(query_words)


def calculate_position_score(rank: int, total: int) -> float:
    """
    Calcula score baseado na posição do resultado.
    Resultados mais bem ranqueados originalmente recebem boost.
    
    Returns:
        Score entre 0 e 1, decaindo exponencialmente
    """
    if total == 0:
        return 0.0
    
    # Decay exponencial: primeiro resultado = 1.0, último = ~0.1
    return 1.0 / (1.0 + rank * 0.5)


def calculate_content_quality_score(content: str) -> float:
    """
    Avalia qualidade do conteúdo baseado em heurísticas.
    
    Critérios:
    - Tamanho adequado (não muito curto, não muito longo)
    - Presença de estrutura (parágrafos, pontuação)
    - Densidade de informação
    
    Returns:
        Score entre 0 e 1
    """
    score = 0.0
    
    # Tamanho ideal: entre 300 e 1500 caracteres
    length = len(content)
    if 300 <= length <= 1500:
        score += 0.4
    elif 150 <= length < 300 or 1500 < length <= 2000:
        score += 0.2
    
    # Presença de estrutura (múltiplas frases)
    sentences = len(re.findall(r'[.!?]+', content))
    if sentences >= 3:
        score += 0.3
    elif sentences >= 1:
        score += 0.15
    
    # Densidade: não muito espaçado, não muito compacto
    words = len(content.split())
    if words > 0:
        chars_per_word = length / words
        if 4 <= chars_per_word <= 8:  # Média razoável em português
            score += 0.3
        elif 3 <= chars_per_word < 4 or 8 < chars_per_word <= 10:
            score += 0.15
    
    return min(score, 1.0)


def rerank_results(
    query: str,
    results: List[Dict],
    weights: Dict[str, float] = None
) -> List[Dict]:
    """
    Re-rankeia resultados usando múltiplos sinais de relevância.
    
    Args:
        query: Pergunta do usuário
        results: Lista de resultados do FAISS (com 'score', 'content', etc)
        weights: Pesos para cada componente do score (opcional)
    
    Returns:
        Lista de resultados re-ranqueados com novo campo 'final_score'
    """
    if not results:
        return results
    
    # Pesos padrão para cada componente
    default_weights = {
        'semantic_similarity': 0.50,  # Score FAISS original
        'keyword_overlap': 0.25,      # Overlap de palavras-chave
        'position': 0.10,             # Posição original
        'content_quality': 0.15       # Qualidade do conteúdo
    }
    
    weights = weights or default_weights
    
    print(f"\n🔄 Re-ranking {len(results)} resultados...")
    print(f"   Pesos: {weights}")
    
    # Calcula scores compostos
    for i, result in enumerate(results):
        # Score semântico (normalizado 0-1, já vem do FAISS)
        semantic_score = result.get('score', 0.0)
        
        # Score de overlap de keywords
        keyword_score = calculate_keyword_overlap(query, result.get('content', ''))
        
        # Score de posição original
        position_score = calculate_position_score(i, len(results))
        
        # Score de qualidade do conteúdo
        quality_score = calculate_content_quality_score(result.get('content', ''))
        
        # Score final ponderado
        final_score = (
            weights['semantic_similarity'] * semantic_score +
            weights['keyword_overlap'] * keyword_score +
            weights['position'] * position_score +
            weights['content_quality'] * quality_score
        )
        
        result['final_score'] = final_score
        result['rerank_details'] = {
            'semantic': semantic_score,
            'keywords': keyword_score,
            'position': position_score,
            'quality': quality_score
        }
        
        print(f"   [{i}] Score: {semantic_score:.3f} → {final_score:.3f} "
              f"(kw:{keyword_score:.2f} pos:{position_score:.2f} qual:{quality_score:.2f})")
    
    # Re-ordena por score final
    reranked = sorted(results, key=lambda x: x['final_score'], reverse=True)
    
    print(f"   ✓ Re-ranking concluído")
    print(f"   Top-3 após re-rank:")
    for i, result in enumerate(reranked[:3]):
        print(f"      {i+1}. {result.get('title', 'Unknown')[:40]} "
              f"(score: {result['final_score']:.3f})")
    
    return reranked
