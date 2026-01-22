# Soluções para Quota do Google Gemini API

> **Atualização:** o backend foi migrado para usar Groq (endpoint OpenAI-compatible) para reduzir bloqueios de quota do Gemini. As estratégias abaixo seguem válidas como referência de mitigação e fallback.

## 🔴 Problema Atual

**Erro:** `429 ResourceExhausted - Quota exceeded`  
**Limite:** 5 requisições/minuto (tier gratuito)  
**Impacto:** Usuários não conseguem fazer mais de 5 perguntas por minuto

## ✅ Soluções Implementadas (Curto Prazo)

### 1. Retry com Exponential Backoff
- **Implementado em:** `backend/rag.py:generate_answer()`
- **Funcionamento:**
  - 3 tentativas automáticas
  - Espera: 2s → 4s → 8s
  - Se falhar após 3 tentativas, retorna mensagem amigável
- **Código:**
```python
for attempt in range(max_retries):
    try:
        response = model.generate_content(prompt)
        break
    except google_exceptions.ResourceExhausted:
        wait_time = retry_delay * (2 ** attempt)
        time.sleep(wait_time)
```

### 2. Mensagem Amigável ao Usuário
- **Frontend:** Card amarelo destacado (AnswerCard.tsx)
- **Backend:** Mensagem clara sobre o limite
- **Conteúdo:**
```
🕐 Limite de requisições atingido
Nosso sistema utiliza o Google Gemini API (tier gratuito: 5 requisições/minuto).
Por favor, aguarde 1 minuto e tente novamente.
💡 Dica: Perguntas já feitas recentemente são respondidas instantaneamente do cache.
```

### 3. Cache de Respostas
- **Já implementado:** `backend/cache.py`
- **Funciona:** Perguntas repetidas não consomem quota
- **Validade:** Configurável (padrão: 1 hora)

---

## 🎯 Soluções de Médio Prazo (Próximos 30 dias)

### 4. Rate Limiting Inteligente
**Implementar:** Limitador no backend para prevenir abuso

```python
# backend/rate_limit.py
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests=4, window=60):
        self.max_requests = max_requests  # 4 (margem de segurança)
        self.window = window  # 60 segundos
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        # Remove requisições antigas
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] 
            if now - t < self.window
        ]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        self.requests[client_ip].append(now)
        return True
```

**Uso em `main.py`:**
```python
limiter = RateLimiter(max_requests=4, window=60)

@app.post("/ask")
async def ask(request: AskRequest, req: Request):
    client_ip = req.client.host
    if not limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Muitas requisições. Aguarde 1 minuto."
        )
    # ... continua
```

### 5. Queue de Requisições
**Implementar:** Fila para processar requisições sequencialmente

```python
# backend/queue.py
import asyncio
from queue import Queue

class RequestQueue:
    def __init__(self):
        self.queue = Queue()
        self.processing = False
    
    async def add(self, question, callback):
        self.queue.put((question, callback))
        if not self.processing:
            await self.process()
    
    async def process(self):
        self.processing = True
        while not self.queue.empty():
            question, callback = self.queue.get()
            await asyncio.sleep(12)  # 60s / 5 = 12s entre chamadas
            result = await callback(question)
            # Retorna resultado via websocket
        self.processing = False
```

### 6. Melhorar Cache Strategy
**Implementar:** Cache mais agressivo

- Cache de embeddings de perguntas (busca semântica no cache)
- TTL maior para perguntas populares
- Pre-cache de perguntas frequentes

```python
# Busca semântica no cache
def search_similar_cached_questions(question: str, threshold=0.9):
    embedder = load_embedder()
    q_emb = embedder.encode(question)
    
    for cached_q, cached_data in cache.items():
        cached_emb = embedder.encode(cached_q)
        similarity = cosine_similarity(q_emb, cached_emb)
        if similarity > threshold:
            return cached_data
    return None
```

---

## 🚀 Soluções de Longo Prazo (Próximos 90 dias)

### 7. Upgrade para Tier Pago do Gemini
**Custo:** ~$7/mês (Pay-as-you-go)  
**Benefícios:**
- 360 requisições/minuto (vs 5)
- 10.000 requisições/dia (vs 50)
- SLA 99.9%

**Como ativar:**
1. Acessar [Google AI Studio](https://aistudio.google.com/)
2. Configurar billing no Google Cloud
3. Atualizar API key

### 8. Modelo Local com Ollama
**Alternativa:** Rodar modelo local (sem limites)

```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Baixar modelo português
ollama pull llama3.2:3b

# Usar no backend
from langchain_community.llms import Ollama
model = Ollama(model="llama3.2:3b")
```

**Prós:**
- Sem custos recorrentes
- Sem rate limits
- Privacidade total

**Contras:**
- Requer servidor com GPU (4GB+ VRAM)
- Qualidade inferior ao Gemini 2.5
- Maior latência

### 9. Híbrido: Fallback Strategy
**Implementar:** Gemini como primário, Ollama como fallback

```python
def generate_answer_hybrid(question, contexts):
    try:
        # Tenta Gemini primeiro
        return generate_answer_gemini(question, contexts)
    except google_exceptions.ResourceExhausted:
        # Fallback para Ollama local
        return generate_answer_ollama(question, contexts)
```

### 10. Clustering de Perguntas
**Implementar:** Agrupar perguntas similares

- Processar perguntas em batch
- 1 chamada Gemini gera múltiplas respostas
- Reduz consumo de quota em 80%

---

## 📊 Monitoramento

### Métricas a Acompanhar
1. **Requisições/minuto** - Quantas chamadas ao Gemini
2. **Cache hit rate** - % de perguntas respondidas do cache
3. **Erros 429** - Frequência de quota exceeded
4. **Latência p95** - Tempo de resposta (incluindo retries)

### Dashboard Sugerido (Grafana/Prometheus)
```python
# backend/metrics.py
from prometheus_client import Counter, Histogram

gemini_requests = Counter('gemini_requests_total', 'Total Gemini API calls')
gemini_errors = Counter('gemini_errors_total', 'Gemini API errors', ['error_type'])
cache_hits = Counter('cache_hits_total', 'Cache hits')
response_time = Histogram('response_time_seconds', 'Response time')
```

---

## 🎯 Recomendação Imediata

**Para resolver o problema AGORA:**

1. ✅ **Implementado:** Retry + mensagens amigáveis
2. ⏳ **Próxima semana:** Rate limiting por IP
3. 💰 **Próximo mês:** Upgrade para tier pago ($7/mês)

**ROI do upgrade pago:**
- Suporta ~50 usuários simultâneos
- Custo: $7/mês
- Alternativa: Servidor GPU para Ollama = $30+/mês

**Decisão:** Upgrade para tier pago é mais econômico e simples.

---

## 📚 Referências

- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Google Cloud Billing](https://console.cloud.google.com/billing)
- [Ollama Documentation](https://ollama.com/docs)
- [FastAPI Rate Limiting](https://github.com/laurentS/slowapi)
