# Garantia de Grounding no Acervo - Sistema RAG

## 🔒 Regra de Ouro

**TODAS as respostas são baseadas EXCLUSIVAMENTE nos documentos PDF do acervo.**

O sistema NUNCA inventa, deduz ou completa informações que não estejam explicitamente presentes nos PDFs indexados.

---

## 🎯 Filosofia do Sistema

### O que o sistema FAZ:
1. ✅ Busca chunks de texto nos PDFs indexados
2. ✅ Encontra os trechos mais relevantes para a pergunta
3. ✅ Reformula linguisticamente esses trechos em linguagem natural
4. ✅ Retorna "Não encontrei" quando a informação não está no acervo

### O que o sistema NÃO FAZ:
1. ❌ Usar conhecimento prévio do Gemini sobre Umbanda
2. ❌ Completar informações parciais com dedução
3. ❌ Inventar exemplos, detalhes ou explicações
4. ❌ Dar respostas genéricas quando o acervo é específico
5. ❌ Adicionar informações de fontes externas

---

## 🛡️ Camadas de Proteção Implementadas

### 1. Prompt Engineering (Camada Primária)

**Localização**: `backend/rag.py`, função `generate_answer()`

**Proteções**:
```python
# Regra fundamental no início do prompt
"**REGRA FUNDAMENTAL**: Você DEVE responder APENAS com informações 
que estão EXPLICITAMENTE presentes nos contextos abaixo. 
Se a informação não estiver nos contextos, responda 'NÃO_ENCONTREI'."
```

**Instruções ao Gemini**:
- Chain-of-Thought: Força verificação explícita se informação está nos contextos
- Exemplos: 3 casos mostrando quando responder e quando retornar NÃO_ENCONTREI
- Regras absolutas: Lista de comportamentos proibidos (inventar, deduzir, supor)
- Validação final: Checklist antes de gerar resposta

### 2. Validação Pós-Geração (Camada Secundária)

**Localização**: `backend/rag.py`, após `model.generate_content()`

**Validações Automáticas**:

1. **Detecção de NÃO_ENCONTREI**:
```python
if "NÃO_ENCONTREI" in answer.upper():
    return "Não encontrei essa informação no acervo..."
```

2. **Resposta muito curta** (possível falha):
```python
if len(answer.strip()) < 20:
    return "Não encontrei essa informação no acervo..."
```

3. **Detecção de alucinações** (frases que indicam conhecimento prévio):
```python
hallucination_indicators = [
    "de acordo com a tradição",
    "na umbanda tradicional",
    "geralmente se diz que",
    "é sabido que",
    ...
]
# Verifica se frase aparece na resposta mas NÃO nos contextos
```

### 3. Limitação de Contextos (Camada Terciária)

**Localização**: `backend/rag.py`, função `search()`

**Proteção**:
- Apenas documentos com `score >= min_sim` (padrão: 0.30) são enviados ao Gemini
- Se não houver contextos relevantes, retorna vazio
- Gemini recebe apenas os top-k chunks (padrão: 8)

```python
if not contexts:
    return "Não encontrei essa informação no acervo..."
```

### 4. Fonte Única de Verdade

**Localização**: `backend/data/pdfs/`

**Garantia**:
- Índice FAISS contém APENAS embeddings dos PDFs nesta pasta
- Metadata JSON rastreia exatamente qual PDF e página cada chunk veio
- Não há mistura com bases de conhecimento externas

---

## 📊 Fluxo de Validação

```
Pergunta do Usuário
        ↓
    BUSCA (FAISS + BM25)
        ↓
    Encontrou chunks? ───[NÃO]──→ "Não encontrei no acervo"
        │
       [SIM]
        ↓
    Score >= min_sim? ──[NÃO]──→ "Não encontrei no acervo"
        │
       [SIM]
        ↓
    PROMPT para Gemini
    (com regras anti-alucinação)
        ↓
    Gemini gera resposta
        ↓
    VALIDAÇÕES PÓS-GERAÇÃO:
    ├─ Contém "NÃO_ENCONTREI"? ──[SIM]──→ "Não encontrei no acervo"
    ├─ Resposta < 20 chars? ─────[SIM]──→ "Não encontrei no acervo"
    ├─ Detectou alucinação? ─────[SIM]──→ ⚠️ Log de alerta
    └─ Tudo OK? ─────────────────[SIM]──→ Retorna resposta
```

---

## 🧪 Como Testar o Grounding

### Teste 1: Pergunta fora do acervo
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual o horário de funcionamento do terreiro?"}'

# Esperado: "Não encontrei essa informação no acervo..."
```

### Teste 2: Informação específica presente
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que é Umbanda?"}'

# Esperado: Resposta baseada nos PDFs, com fontes listadas
# Verificar: Conferir se informações batem com PDFs originais
```

### Teste 3: Tentativa de alucinação
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual a cor preferida de Exu segundo a tradição?"}'

# Se PDFs não mencionam "cor preferida":
#   Esperado: "Não encontrei essa informação no acervo..."
# Se PDFs mencionam cores de Exu:
#   Esperado: Resposta citando APENAS as cores mencionadas nos PDFs
```

### Teste 4: Verificação manual
1. Fazer pergunta específica
2. Anotar resposta do sistema
3. Abrir PDFs manualmente
4. Buscar (Ctrl+F) os termos mencionados na resposta
5. Confirmar que TUDO está presente nos PDFs

---

## 🔍 Logs de Monitoramento

**Ativar logs detalhados**:
```python
# Em backend/rag.py
print(f"📄 Contextos enviados ao Gemini: {len(contexts)}")
print(f"✅ Resposta gerada ({len(answer)} caracteres)")
print(f"⚠️ ALERTA: Possível alucinação detectada - frase '{indicator}'")
```

**O que observar nos logs**:
- ✅ "Resposta gerada" → OK
- ⚠️ "Possível alucinação detectada" → Investigar
- 🔴 "Gemini retornou NÃO_ENCONTREI" → Informação não está no acervo (correto)

---

## 🚨 Protocolo de Emergência

**Se suspeitar que o sistema está inventando respostas**:

### 1. Verificação Imediata
```bash
# Ver últimas respostas no dashboard admin
https://aiye-chat.vercel.app/admin

# Filtrar por rating baixo (usuários reclamando de respostas erradas)
```

### 2. Análise de Logs
```bash
# HF Spaces logs
https://huggingface.co/spaces/dev-mateus/backend-aiye/logs

# Procurar por: "⚠️ ALERTA: Possível alucinação"
```

### 3. Desativação Temporária de Features
Se problema persistir, desativar melhorias uma por uma:

```python
# Em backend/app.py
answer, contexts = ask_with_cache(
    question=question,
    use_query_expansion=False,  # Desativa query expansion
    use_hybrid=False,            # Desativa hybrid search
    use_reranking=False          # Desativa re-ranking
)
```

### 4. Fallback para Versão Antiga
```bash
# Reverter para commit anterior
git revert HEAD
git push origin main
git push space main
```

---

## ✅ Checklist de Validação para Novas Features

Antes de adicionar qualquer nova funcionalidade ao RAG:

- [ ] A feature melhora a BUSCA nos PDFs ou a REFORMULAÇÃO linguística?
- [ ] A feature NÃO permite adicionar informações externas aos PDFs?
- [ ] Testei com perguntas fora do acervo? (deve retornar "não encontrei")
- [ ] Testei com perguntas no acervo? (resposta bate com PDFs?)
- [ ] Adicionei logs para detectar possíveis alucinações?
- [ ] Documentei claramente que a feature respeita grounding?

---

## 📝 Responsabilidades por Módulo

| Módulo | Responsabilidade | Grounding? |
|--------|------------------|------------|
| `chunking.py` | Dividir PDFs em chunks | ✅ Apenas processa PDFs |
| `hybrid_search.py` | Combinar busca vetorial + keywords | ✅ Apenas reordena chunks existentes |
| `query_expansion.py` | Reformular PERGUNTA do usuário | ✅ Apenas reformula query, não resposta |
| `reranker.py` | Reordenar chunks por relevância | ✅ Apenas reordena chunks existentes |
| `cache.py` | Armazenar respostas já geradas | ✅ Cache de respostas que já passaram por validação |
| `rag.py::search()` | Buscar chunks no FAISS | ✅ Busca apenas no índice de PDFs |
| `rag.py::generate_answer()` | Reformular chunks em linguagem natural | ⚠️ **CRÍTICO** - Único ponto onde Gemini pode alucinar |

---

## 🎓 Entendendo o Papel do Gemini

### ❌ Gemini NÃO é:
- Fonte de conhecimento sobre Umbanda
- Especialista que completa informações
- Base de dados de práticas e tradições

### ✅ Gemini É:
- **Reformulador linguístico**: Pega chunks técnicos e torna texto fluido
- **Organizador**: Estrutura informações em parágrafos e listas
- **Sintetizador**: Combina múltiplos chunks em resposta coesa

### Analogia:
```
PDFs = Biblioteca de referência (fonte única de verdade)
FAISS = Índice da biblioteca (encontra páginas relevantes)
Gemini = Bibliotecário (reformula páginas em linguagem clara)

O bibliotecário NUNCA adiciona informações que não estão nos livros!
```

---

## 🔗 Rastreabilidade

**Cada resposta inclui**:
- Chunks originais usados (no backend)
- Scores de relevância
- Documento fonte e páginas
- Metadata do chunking

**Frontend mostra**:
- Lista de fontes (SourceList component)
- Documento + páginas de cada fonte
- Link para PDF original (se configurado)

**Isso permite**:
- Usuário verificar informação no PDF original
- Auditoria de respostas
- Detecção de inconsistências

---

## 📞 Contato em Caso de Problemas

**Se detectar que o sistema está inventando respostas**:

1. Abrir issue no GitHub com:
   - Pergunta feita
   - Resposta recebida
   - Verificação manual nos PDFs (print ou citação)
   - Logs do backend (se possível)

2. Notificar administrador imediatamente

3. Considerar desativar sistema até correção

---

**Última atualização**: 26 de novembro de 2025  
**Versão**: 2.0.0  
**Status**: ✅ Grounding rigorosamente validado
