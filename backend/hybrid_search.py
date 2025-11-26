"""
Hybrid Search: Combina busca vetorial (dense) + busca por palavras-chave (sparse/BM25).

Benefícios:
- Dense search (FAISS): Captura similaridade semântica
- Sparse search (BM25): Captura matches exatos de keywords
- Hybrid: Combina o melhor dos dois mundos (recall + precision)

Técnica: Reciprocal Rank Fusion (RRF) para combinar rankings
"""

from typing import List, Dict, Tuple
from collections import Counter
import math
import re


class BM25:
    """
    Implementação do algoritmo BM25 (Best Matching 25) para ranking de documentos.
    
    BM25 é o estado da arte em busca por keywords, superior ao TF-IDF.
    Considera:
    - Term frequency (TF): Quantas vezes termo aparece
    - Inverse document frequency (IDF): Raridade do termo
    - Document length normalization: Penaliza docs muito longos
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Args:
            k1: Controla saturação de term frequency (1.2-2.0 típico)
            b: Controla normalização de comprimento (0-1, sendo 0.75 ótimo)
        """
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        self.avgdl = 0
    
    def fit(self, corpus: List[str]):
        """
        Indexa o corpus para busca BM25.
        
        Args:
            corpus: Lista de textos (um por documento)
        """
        self.corpus = corpus
        self.doc_len = [len(doc.split()) for doc in corpus]
        self.avgdl = sum(self.doc_len) / len(self.doc_len) if self.doc_len else 0
        
        # Calcula document frequency para cada termo
        df = {}
        for doc in corpus:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                df[token] = df.get(token, 0) + 1
        
        # Calcula IDF para cada termo
        num_docs = len(corpus)
        for term, freq in df.items():
            # IDF suavizado (evita divisão por zero)
            self.idf[term] = math.log((num_docs - freq + 0.5) / (freq + 0.5) + 1)
        
        print(f"✓ BM25 indexado: {num_docs} documentos, {len(self.idf)} termos únicos")
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokeniza texto (lowercase, remove pontuação, split).
        """
        # Remove pontuação e converte para lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Remove stopwords básicas em português
        stopwords = {
            'a', 'o', 'e', 'de', 'da', 'do', 'em', 'um', 'uma', 'os', 'as',
            'para', 'com', 'por', 'é', 'à', 'ao', 'na', 'no', 'dos', 'das',
            'que', 'se', 'como', 'mais', 'mas', 'foi', 'são', 'seu', 'sua'
        }
        tokens = [t for t in text.split() if t and t not in stopwords and len(t) > 2]
        return tokens
    
    def get_scores(self, query: str) -> List[float]:
        """
        Calcula score BM25 da query para cada documento.
        
        Returns:
            Lista de scores (um por documento, mesma ordem do corpus)
        """
        query_tokens = self._tokenize(query)
        scores = [0.0] * len(self.corpus)
        
        for i, doc in enumerate(self.corpus):
            doc_tokens = self._tokenize(doc)
            doc_len = self.doc_len[i]
            
            # Conta frequência de cada termo da query no documento
            term_freqs = Counter(doc_tokens)
            
            score = 0.0
            for term in query_tokens:
                if term not in self.idf:
                    continue
                
                tf = term_freqs.get(term, 0)
                idf = self.idf[term]
                
                # Fórmula BM25
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))
                score += idf * (numerator / denominator)
            
            scores[i] = score
        
        return scores
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Busca top-k documentos mais relevantes para a query.
        
        Returns:
            Lista de tuplas (doc_index, score) ordenadas por score
        """
        scores = self.get_scores(query)
        
        # Ordena por score decrescente
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        
        # Retorna apenas top-k com score > 0
        return [(idx, score) for idx, score in ranked[:top_k] if score > 0]


def reciprocal_rank_fusion(
    rankings: List[List[Tuple[int, float]]],
    k: int = 60
) -> List[Tuple[int, float]]:
    """
    Reciprocal Rank Fusion (RRF): Combina múltiplos rankings em um só.
    
    RRF é superior a média ponderada pois:
    - Não depende de normalização de scores
    - Robusto a outliers
    - Funciona bem mesmo com rankings de escalas diferentes
    
    Fórmula: RRF(d) = Σ 1/(k + rank(d))
    
    Args:
        rankings: Lista de rankings (cada um é lista de (doc_id, score))
        k: Constante de suavização (60 é ótimo empiricamente)
    
    Returns:
        Ranking combinado (doc_id, rrf_score)
    """
    rrf_scores = {}
    
    for ranking in rankings:
        for rank, (doc_id, _) in enumerate(ranking):
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = 0.0
            # Adiciona score RRF (1 / (k + rank))
            rrf_scores[doc_id] += 1.0 / (k + rank)
    
    # Ordena por RRF score decrescente
    combined = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    
    return combined


class HybridSearch:
    """
    Sistema de busca híbrida que combina:
    - Dense search (FAISS): Similaridade semântica vetorial
    - Sparse search (BM25): Matching de keywords
    
    Usa Reciprocal Rank Fusion para combinar resultados.
    """
    
    def __init__(self, alpha: float = 0.5):
        """
        Args:
            alpha: Peso para dense search (1-alpha para sparse)
                   0.5 = balanceado, >0.5 favorece semântica, <0.5 favorece keywords
        """
        self.alpha = alpha
        self.bm25 = BM25()
        self.corpus = []
        self.metadata = []
    
    def index_documents(self, documents: List[Dict]):
        """
        Indexa documentos para busca híbrida.
        
        Args:
            documents: Lista de dicts com 'content' e outros metadados
        """
        self.corpus = [doc['content'] for doc in documents]
        self.metadata = documents
        
        # Indexa BM25
        self.bm25.fit(self.corpus)
        
        print(f"✓ Hybrid Search indexado: {len(self.corpus)} documentos")
    
    def search(
        self,
        query: str,
        dense_results: List[Dict],
        top_k: int = 8
    ) -> List[Dict]:
        """
        Busca híbrida que combina resultados densos (FAISS) com BM25.
        
        Args:
            query: Pergunta do usuário
            dense_results: Resultados do FAISS (já filtrados por min_sim)
            top_k: Número de resultados finais
        
        Returns:
            Resultados re-ranqueados combinando dense + sparse
        """
        if not self.corpus:
            # Se BM25 não está indexado, retorna apenas dense results
            return dense_results[:top_k]
        
        # 1. Ranking dense (FAISS)
        dense_ranking = [(i, res['score']) for i, res in enumerate(dense_results)]
        
        # 2. Ranking sparse (BM25)
        # Precisa mapear índices dos dense_results para corpus BM25
        sparse_scores = self.bm25.get_scores(query)
        
        # Cria mapeamento de content para índice em dense_results
        content_to_dense_idx = {
            res['content']: i for i, res in enumerate(dense_results)
        }
        
        sparse_ranking = []
        for corpus_idx, score in enumerate(sparse_scores):
            if score > 0:
                content = self.corpus[corpus_idx]
                if content in content_to_dense_idx:
                    dense_idx = content_to_dense_idx[content]
                    sparse_ranking.append((dense_idx, score))
        
        # Ordena sparse por score
        sparse_ranking.sort(key=lambda x: x[1], reverse=True)
        
        # 3. Combina com RRF ponderado
        if self.alpha == 1.0:
            # Apenas dense
            combined = dense_ranking
        elif self.alpha == 0.0:
            # Apenas sparse
            combined = sparse_ranking
        else:
            # Ajusta rankings baseado em alpha
            # Alpha alto = mais peso para dense
            dense_weight = int(self.alpha * 100)
            sparse_weight = int((1 - self.alpha) * 100)
            
            # Replica rankings para dar mais peso
            weighted_rankings = (
                [dense_ranking] * dense_weight +
                [sparse_ranking] * sparse_weight
            )
            
            combined = reciprocal_rank_fusion(weighted_rankings)
        
        # 4. Retorna top-k resultados
        result_indices = [idx for idx, score in combined[:top_k]]
        
        # Adiciona hybrid_score aos resultados
        hybrid_results = []
        for idx, hybrid_score in combined[:top_k]:
            if idx < len(dense_results):
                result = dense_results[idx].copy()
                result['hybrid_score'] = hybrid_score
                result['bm25_boosted'] = idx in [i for i, _ in sparse_ranking[:5]]
                hybrid_results.append(result)
        
        print(f"🔀 Hybrid Search: {len(dense_results)} dense → {len(hybrid_results)} hybrid")
        
        return hybrid_results


def create_hybrid_searcher(chunks_metadata: List[Dict], alpha: float = 0.6) -> HybridSearch:
    """
    Factory function para criar HybridSearch e indexar documentos.
    
    Args:
        chunks_metadata: Lista de chunks com metadata
        alpha: Peso para dense search (0.6 = 60% semântica, 40% keywords)
    
    Returns:
        HybridSearch instance pronta para uso
    """
    searcher = HybridSearch(alpha=alpha)
    searcher.index_documents(chunks_metadata)
    return searcher
