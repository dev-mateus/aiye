# Cache e Re-ranking - Melhorias RAG

## Visão Geral

Este documento descreve as melhorias implementadas no sistema RAG (Retrieval-Augmented Generation) para otimizar **desempenho** (cache) e **qualidade** (re-ranking) das respostas.

## 1. Cache de Respostas (LRU)

### Objetivo
Reduzir latência e custos de API ao armazenar respostas para perguntas frequentes.

### Implementação
**Arquivo**: `backend/cache.py`

**Classe Principal**: `ResponseCache`

**Características**:
- **Algoritmo**: LRU (Least Recently Used) - Remove respostas menos usadas quando atinge capacidade máxima
- **Capacidade**: 100 respostas (configurável via `max_size`)
- **Chave**: MD5 hash da pergunta normalizada (lowercase, sem pontuação, espaços normalizados)
- **Armazenamento**: Em memória (dict Python)
- **Persistência**: Não persistente (reinicia com cada deploy)

**Normalização de Perguntas**:
```python
"O que é Umbanda?" → "o que e umbanda"
"O QUE É UMBANDA?!!" → "o que e umbanda"
```
Isso permite que variações da mesma pergunta compartilhem o mesmo cache.

**Métodos**:
- `get(question)`: Retorna `{'answer': str, 'contexts': list, 'original_question': str}` ou `None`
- `set(question, answer, contexts)`: Armazena resposta, evita duplicatas se existir
- `stats()`: Retorna `{'size': int, 'max_size': int, 'usage_percent': float}`
- `clear()`: Limpa todo o cache

**Singleton**:
```python
from backend.cache import get_response_cache
cache = get_response_cache()  # Sempre retorna a mesma instância global
```

### Logs
```
Cache HIT: "o que e umbanda" (MD5: a1b2c3...)
Cache MISS: "quem sao os orixas" (MD5: d4e5f6...)
✓ Resposta armazenada no cache (1/100)
⚠️ Cache cheio! Removendo entrada menos usada: "pergunta antiga"
```

### Endpoint de Monitoramento
**GET** `/cache/stats`

**Resposta**:
```json
{
  "size": 42,
  "max_size": 100,
  "usage_percent": 42.0
}
```

### Configuração
Para alterar o tamanho do cache, edite `backend/rag.py`:
```python
cache = get_response_cache(max_size=200)  # Aumenta para 200 respostas
```

## 2. Re-ranking Multi-Signal

### Objetivo
Melhorar a relevância dos documentos recuperados além da similaridade semântica pura do FAISS.

### Implementação
**Arquivo**: `backend/reranker.py`

**Função Principal**: `rerank_results(query, results)`

**Sinais de Relevância** (4 componentes):

#### 1. Similaridade Semântica (50%)
- Score original do FAISS (produto interno normalizado)
- Base: embedding vetorial da pergunta vs contextos

#### 2. Sobreposição de Keywords (25%)
- Remove stopwords em português (de, para, com, etc.)
- Conta palavras da pergunta que aparecem no conteúdo
- Fórmula: `overlap_count / max(query_words, content_words)`

#### 3. Posição Original (10%)
- Privilegia documentos que FAISS ranqueou no topo
- Fórmula: `1.0 / (1 + rank * 0.5)` (decaimento exponencial)

#### 4. Qualidade do Conteúdo (15%)
Heurísticas para textos bem estruturados:
- **Comprimento**: 300-1500 caracteres (ideal para contexto)
  - 0.4 pontos se ideal
  - 0.2 pontos se 150-300 ou 1500-2000
  - 0.0 se muito curto/longo
- **Estrutura**: Número de sentenças
  - 0.3 pontos se 3+ sentenças
  - 0.15 pontos se 1-2 sentenças
- **Densidade**: Caracteres por palavra (média português = 5)
  - 0.3 pontos se 4-8 chars/palavra
  - 0.0 caso contrário

### Fórmula Final
```python
final_score = (
    semantic * 0.50 +
    keyword_overlap * 0.25 +
    position * 0.10 +
    content_quality * 0.15
)
```

### Logs Detalhados
```
🔄 Re-ranking 8 resultados para query: "o que é umbanda"

Resultado 1 (original rank 0):
  Semantic: 0.8500
  Keywords: 0.6667 (4/6 palavras)
  Position: 1.0000 (rank 0)
  Quality: 0.8500 (length=0.4, structure=0.3, density=0.15)
  FINAL: 0.7958

[Scores originais]
  0.8500 → 0.7958 ✓
  0.8200 → 0.7123 ↓
  ...

Re-ranking completo! Top resultado: UMBANDA: religião do Brasil (pp. 12-14)
```

### Metadados Adicionados
Cada resultado retornado inclui:
```python
{
  "content": "...",
  "title": "...",
  "page_start": 12,
  "page_end": 14,
  "score": 0.85,  # Score semântico original
  "final_score": 0.7958,  # Score após re-ranking
  "rerank_details": {
    "semantic_similarity": 0.85,
    "keyword_overlap": 0.6667,
    "position_score": 1.0,
    "content_quality": 0.85
  }
}
```

### Ativação/Desativação
**Padrão**: Re-ranking ativado automaticamente

**Para desativar**:
```python
# Em backend/rag.py, função ask_with_cache()
answer, contexts = ask_with_cache(
    question=question,
    use_reranking=False  # Desativa re-ranking
)
```

## 3. Integração Completa

### Fluxo de Requisição
```
POST /ask {"question": "o que é umbanda?"}
  ↓
1. ask_with_cache()
  ↓
2. cache.get("o que e umbanda")  # Normaliza e busca
  ↓
3a. [CACHE HIT] → Retorna resposta instantaneamente ✓
  ↓
3b. [CACHE MISS] → search() com re-ranking
  ↓
4. FAISS: Busca top-8 documentos (semantic similarity)
  ↓
5. rerank_results(): Reordena com 4 sinais
  ↓
6. generate_answer(): Gemini sintetiza resposta
  ↓
7. cache.set(): Armazena para próxima vez
  ↓
8. Retorna resposta + fontes + metadata
```

### Endpoints Afetados
- **POST** `/ask` - Usa cache + re-ranking
- **POST** `/ask-raw` - Usa cache + re-ranking
- **GET** `/cache/stats` - Estatísticas do cache (novo)

## 4. Testes e Validação

### Testar Cache
```bash
# 1ª requisição (CACHE MISS)
curl -X POST https://dev-mateus-backend-aiye.hf.space/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "o que é umbanda?"}'

# Verifique logs: "Cache MISS: o que e umbanda"

# 2ª requisição (CACHE HIT - deve ser instantânea)
curl -X POST https://dev-mateus-backend-aiye.hf.space/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O QUE É UMBANDA?!!"}'  # Variação normalizada

# Verifique logs: "Cache HIT: o que e umbanda"
```

### Verificar Estatísticas
```bash
curl https://dev-mateus-backend-aiye.hf.space/cache/stats
```

### Testar Re-ranking
Compare scores nos logs:
```
[Scores originais]  # Antes do re-ranking
  0.8500 → 0.7958 ✓  # Este melhorou (mais keywords)
  0.8200 → 0.7123 ↓  # Este piorou (menos keywords)
```

Documentos com mais keywords da pergunta sobem no ranking.

## 5. Impacto Esperado

### Cache
- **Latência**: ~2000ms → ~50ms para perguntas repetidas
- **Custos**: Reduz chamadas à API Gemini
- **Hit Rate Esperado**: 20-40% (depende de perguntas repetidas)

### Re-ranking
- **Qualidade**: Melhora relevância em 10-30%
- **Precisão**: Documentos com keywords corretas sobem
- **Recall**: Mantém cobertura (não remove documentos)

## 6. Limitações e Próximos Passos

### Limitações Atuais
- Cache não persiste entre deploys (em memória)
- Stopwords apenas em português
- Heurísticas de qualidade simples

### Melhorias Futuras
- [ ] Cache persistente (Redis/Memcached)
- [ ] Re-ranking com modelo cross-encoder (mais lento, mais preciso)
- [ ] Cache TTL (expiração por tempo)
- [ ] Métricas de hit rate no admin dashboard
- [ ] A/B testing cache on/off

## 7. Troubleshooting

### Cache não está funcionando
```python
# Verifique se está ativado
answer, contexts = ask_with_cache(use_cache=True)

# Verifique logs para "Cache HIT/MISS"
# Se não aparecer, verifique imports em app.py
```

### Re-ranking piora resultados
```python
# Desative temporariamente
answer, contexts = ask_with_cache(use_reranking=False)

# Ajuste pesos em backend/reranker.py linha ~140:
final_score = (
    semantic * 0.70 +  # Aumenta peso semântico
    keyword * 0.20 +   # Reduz keywords
    position * 0.05 +
    quality * 0.05
)
```

### Cache cheio muito rápido
```python
# Aumente capacidade em backend/rag.py
cache = get_response_cache(max_size=500)
```

---

**Autor**: Implementado em 2024  
**Versão**: 1.0  
**Arquivos**: `backend/cache.py`, `backend/reranker.py`, `backend/rag.py`, `backend/app.py`
