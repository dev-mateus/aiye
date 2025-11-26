"""
Sistema de cache LRU para respostas RAG.
Armazena perguntas e respostas em memória para reduzir latência e custos de API.
"""

from functools import lru_cache
from typing import Optional
import hashlib


class ResponseCache:
    """Cache LRU para respostas do RAG."""
    
    def __init__(self, max_size: int = 100):
        """
        Inicializa o cache com tamanho máximo.
        
        Args:
            max_size: Número máximo de respostas em cache
        """
        self.max_size = max_size
        self._cache: dict[str, dict] = {}
        self._access_order: list[str] = []  # Para LRU
    
    def _normalize_question(self, question: str) -> str:
        """
        Normaliza a pergunta para melhorar cache hits.
        Remove pontuação extra, normaliza espaços, lowercase.
        """
        import re
        # Lowercase e remove espaços extras
        normalized = question.lower().strip()
        # Remove pontuação múltipla
        normalized = re.sub(r'[?.!]+', '', normalized)
        # Normaliza espaços
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    def _get_key(self, question: str) -> str:
        """
        Gera chave de cache usando hash da pergunta normalizada.
        """
        normalized = self._normalize_question(question)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get(self, question: str) -> Optional[dict]:
        """
        Recupera resposta do cache se existir.
        
        Returns:
            dict com 'answer' e 'contexts' ou None se não encontrado
        """
        key = self._get_key(question)
        
        if key in self._cache:
            # Atualiza ordem de acesso (LRU)
            self._access_order.remove(key)
            self._access_order.append(key)
            
            print(f"✓ Cache HIT: '{question[:50]}...'")
            return self._cache[key]
        
        print(f"✗ Cache MISS: '{question[:50]}...'")
        return None
    
    def set(self, question: str, answer: str, contexts: list[dict]):
        """
        Armazena resposta no cache.
        
        Args:
            question: Pergunta original
            answer: Resposta gerada
            contexts: Contextos usados para gerar a resposta
        """
        key = self._get_key(question)
        
        # Se cache está cheio, remove o item menos recente (LRU)
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
            print(f"⚠ Cache EVICT (LRU): removido item antigo")
        
        # Adiciona/atualiza no cache
        self._cache[key] = {
            "answer": answer,
            "contexts": contexts,
            "original_question": question
        }
        
        # Atualiza ordem de acesso
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        print(f"✓ Cache SET: '{question[:50]}...' (total: {len(self._cache)})")
    
    def clear(self):
        """Limpa todo o cache."""
        self._cache.clear()
        self._access_order.clear()
        print("✓ Cache limpo")
    
    def stats(self) -> dict:
        """Retorna estatísticas do cache."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "usage_percent": (len(self._cache) / self.max_size) * 100 if self.max_size > 0 else 0
        }


# Instância global do cache (singleton)
_response_cache: Optional[ResponseCache] = None


def get_response_cache(max_size: int = 100) -> ResponseCache:
    """
    Retorna a instância global do cache de respostas.
    
    Args:
        max_size: Tamanho máximo do cache (usado apenas na primeira chamada)
    
    Returns:
        ResponseCache singleton
    """
    global _response_cache
    if _response_cache is None:
        _response_cache = ResponseCache(max_size=max_size)
        print(f"✓ Cache de respostas inicializado (max_size={max_size})")
    return _response_cache
