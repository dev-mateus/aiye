"""
Query Expansion: Expande a query do usuário com termos relacionados.

⚠️ IMPORTANTE - GROUNDING NO ACERVO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Este módulo APENAS reformula a PERGUNTA do usuário para melhorar a busca.
NÃO gera respostas, NÃO adiciona informações, NÃO inventa conteúdo.

Função: Ajudar a ENCONTRAR mais documentos relevantes no acervo.
Exemplo:
  - Usuário pergunta: "O que é Orixá?"
  - Expansion: ["O que é Orixá?", "O que são Orixás?", "Significado de divindades"]
  - Resultado: Busca no FAISS com 3 queries diferentes
  - Benefício: Encontra mais chunks relevantes no acervo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Benefícios:
- Melhora recall ao encontrar documentos com terminologia diferente
- Captura sinônimos e termos relacionados
- Lida com variações linguísticas (Orixás vs Orishas, etc.)

Estratégias:
1. LLM-based expansion (Gemini): Gera variações semânticas DA PERGUNTA
2. Domain-specific synonyms: Dicionário de termos de Umbanda
3. Query reformulation: Reformula query ambígua
"""

from typing import List, Dict, Optional
# import google.generativeai as genai  # Desabilitado - migrando para Groq
from . import settings


# Dicionário de sinônimos específicos do domínio de Umbanda
UMBANDA_SYNONYMS = {
    "orixá": ["orixás", "orishas", "divindades", "entidades"],
    "exu": ["exús", "compadre", "guardião"],
    "pomba gira": ["pombagira", "maria padilha", "moça"],
    "preto velho": ["pretos velhos", "vovô", "vovó", "pai", "mãe"],
    "caboclo": ["caboclos", "índio", "indígena"],
    "erva": ["ervas", "folha", "folhas", "planta", "plantas"],
    "terreiro": ["terreiros", "casa", "centro", "templo"],
    "gira": ["giras", "trabalho", "sessão"],
    "incorporação": ["incorporar", "virar", "baixar", "manifestar"],
    "oferenda": ["oferendas", "ebó", "despacho"],
    "pontos": ["cantigas", "cantos", "toadas"],
    "ogum": ["oguns", "guerreiro"],
    "oxossi": ["oxóssi", "caçador"],
    "iemanjá": ["yemanjá", "rainha do mar", "mãe d'água"],
    "oxum": ["oxún", "senhora das águas doces"],
    "xangô": ["shangô", "rei"],
    "iansã": ["yansã", "oiá", "senhora dos ventos"],
    "oxalá": ["oxalah", "pai maior"],
    "umbanda": ["religião", "doutrina", "espiritismo"],
}


def expand_query_with_synonyms(query: str) -> List[str]:
    """
    Expande query com sinônimos do domínio de Umbanda.
    
    Args:
        query: Pergunta original do usuário
    
    Returns:
        Lista de variações da query (inclui original)
    """
    query_lower = query.lower()
    expanded = [query]  # Sempre inclui original
    
    for term, synonyms in UMBANDA_SYNONYMS.items():
        if term in query_lower:
            # Cria variações substituindo o termo por sinônimos
            for synonym in synonyms[:2]:  # Limita a 2 sinônimos por termo
                expanded_query = query_lower.replace(term, synonym)
                if expanded_query not in [e.lower() for e in expanded]:
                    expanded.append(expanded_query.capitalize())
    
    return expanded[:3]  # Retorna no máximo 3 variações


def expand_query_with_llm(query: str) -> List[str]:
    """
        Expande query usando LLM para gerar variações semânticas.
    
        ⚠️ TEMPORARIAMENTE DESABILITADO - Em migração para Groq
    
    Args:
        query: Pergunta original do usuário
    
    Returns:
        Lista de variações (inclui original)
    """
    if not settings.GOOGLE_API_KEY:
           # LLM expansion desabilitado temporariamente
           return [query]
    
    try:
           # TODO: Reimplementar com Groq quando necessário
           # Por enquanto, usa apenas sinônimos
           return [query]
        
           # Código original comentado para futura migração:
           # genai.configure(api_key=settings.GOOGLE_API_KEY)
           # model = genai.GenerativeModel("gemini-2.5-flash")
           # 
           # prompt = f"""Você é um especialista em Umbanda. Dada a pergunta do usuário, gere 2 reformulações alternativas que capturem a mesma intenção mas com palavras diferentes.
            # 
            # PERGUNTA ORIGINAL:
            # {query}
            # 
            # INSTRUÇÕES:
            # 1. Mantenha o significado e intenção originais
            # 2. Use sinônimos e termos relacionados ao contexto de Umbanda
            # 3. Seja conciso (máximo 15 palavras por reformulação)
            # 4. Uma reformulação pode ser mais específica, outra mais geral
            # 5. Retorne apenas as 2 reformulações, separadas por |
            # 
            # EXEMPLO:
            # Pergunta: "O que são oferendas?"
            # Reformulações: "Qual o significado de ebós e despachos?|Como funcionam as entregas aos Orixás?"
            # 
            # REFORMULAÇÕES:"""
            # 
            # response = model.generate_content(prompt)
            # reformulations_text = response.text.strip()
            # 
            # # Parse reformulações (separadas por |)
            # reformulations = [r.strip() for r in reformulations_text.split('|')]
            # reformulations = [r for r in reformulations if r and len(r) > 5][:2]
            # 
            # # Combina original + reformulações
            # all_queries = [query] + reformulations
            # 
            # print(f"🔄 Query expandida: '{query}' → {len(all_queries)} variações")
            # for i, q in enumerate(all_queries[1:], 1):
            #     print(f"   {i}. {q}")
            # 
            # return all_queries
        
    except Exception as e:
        print(f"⚠️ Erro ao expandir query com LLM: {e}")
        return [query]


def expand_query_hybrid(
    query: str,
    use_llm: bool = settings.ENABLE_LLM_EXPANSION,
    use_synonyms: bool = True
) -> List[str]:
    """
    Combina expansão por sinônimos e LLM.
    
    Args:
        query: Pergunta original
        use_llm: Se True, usa Gemini para expansão
        use_synonyms: Se True, usa dicionário de sinônimos
    
    Returns:
        Lista de queries expandidas (deduplicated)
    """
    expanded_queries = {query}  # Set para evitar duplicatas
    
    if use_synonyms:
        synonym_queries = expand_query_with_synonyms(query)
        expanded_queries.update(synonym_queries)
    
    if use_llm:
        llm_queries = expand_query_with_llm(query)
        expanded_queries.update(llm_queries)
    
    # Retorna como lista (máximo 5 queries)
    return list(expanded_queries)[:5]


def should_expand_query(query: str) -> bool:
    """
    Determina se vale a pena expandir a query.
    
    Queries curtas e genéricas se beneficiam mais de expansão.
    Queries específicas e longas podem piorar com expansão.
    
    Args:
        query: Pergunta do usuário
    
    Returns:
        True se deve expandir, False caso contrário
    """
    words = query.split()
    
    # Não expande queries muito curtas (< 3 palavras)
    if len(words) < 3:
        return False
    
    # Não expande queries muito longas (> 15 palavras)
    if len(words) > 15:
        return False
    
    # Não expande queries que já são muito específicas
    specific_indicators = [
        "como fazer", "passo a passo", "exemplo de",
        "diferença entre", "quando usar", "por que"
    ]
    query_lower = query.lower()
    if any(indicator in query_lower for indicator in specific_indicators):
        return False
    
    # Expande queries genéricas
    generic_indicators = [
        "o que é", "o que são", "qual", "quais",
        "significado", "definição", "conceito"
    ]
    if any(indicator in query_lower for indicator in generic_indicators):
        return True
    
    # Por padrão, expande queries de tamanho médio
    return 3 <= len(words) <= 10


class QueryExpander:
    """
    Classe para gerenciar expansão de queries com cache.
    """
    
    def __init__(self, use_llm: bool = True, use_synonyms: bool = True):
        self.use_llm = use_llm
        self.use_synonyms = use_synonyms
        self.cache = {}  # Cache de expansões
    
    def expand(self, query: str, force: bool = False) -> List[str]:
        """
        Expande query (com cache).
        
        Args:
            query: Pergunta original
            force: Se True, força expansão mesmo se heurística diz não
        
        Returns:
            Lista de queries (inclui original)
        """
        # Verifica cache
        if query in self.cache:
            print(f"💾 Query expansion cache HIT: {query}")
            return self.cache[query]
        
        # Decide se deve expandir
        if not force and not should_expand_query(query):
            print(f"⏭️ Query expansion skipped: {query}")
            return [query]
        
        # Expande
        expanded = expand_query_hybrid(
            query,
            use_llm=self.use_llm,
            use_synonyms=self.use_synonyms
        )
        
        # Armazena em cache
        self.cache[query] = expanded
        
        return expanded
    
    def clear_cache(self):
        """Limpa cache de expansões."""
        self.cache.clear()
        print("🧹 Query expansion cache limpo")


# Singleton global
_query_expander: Optional[QueryExpander] = None


def get_query_expander(
    use_llm: bool = True,
    use_synonyms: bool = True
) -> QueryExpander:
    """
    Retorna instância singleton do QueryExpander.
    """
    global _query_expander
    if _query_expander is None:
        _query_expander = QueryExpander(use_llm=use_llm, use_synonyms=use_synonyms)
        print("✓ QueryExpander inicializado")
    return _query_expander
