# Sistema de Avaliação de Respostas

## Visão Geral

O sistema de avaliação permite que os usuários avaliem a qualidade das respostas do chatbot usando uma escala de 1 a 5 estrelas, com a opção de adicionar comentários. Os feedbacks são armazenados para análise futura e melhoria contínua do sistema.

## Arquitetura

### Backend

#### Modelo de Dados (`backend/models.py`)

```python
class FeedbackRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    answer: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)  # 1-5 estrelas
    comment: Optional[str] = Field(None, max_length=500)
```

**Validações:**
- `question`: 1-1000 caracteres (obrigatório)
- `answer`: mínimo 1 caractere (obrigatório)
- `rating`: 1-5 (obrigatório)
- `comment`: máximo 500 caracteres (opcional)

#### Endpoint (`backend/main.py`)

**POST /feedback**

Recebe e armazena avaliações dos usuários.

**Request Body:**
```json
{
  "question": "O que é Umbanda?",
  "answer": "Umbanda é uma religião brasileira...",
  "rating": 5,
  "comment": "Resposta muito clara e completa!"
}
```

**Response (Success - 200):**
```json
{
  "status": "success",
  "message": "Feedback salvo com sucesso"
}
```

**Response (Error - 500):**
```json
{
  "detail": "Erro ao salvar feedback: ..."
}
```

#### Armazenamento

Os feedbacks são salvos em `backend/data/feedback.json` com a seguinte estrutura:

```json
[
  {
    "timestamp": "2025-06-04T14:30:00.000000",
    "question": "O que é Umbanda?",
    "answer": "Umbanda é uma religião brasileira...",
    "rating": 5,
    "comment": "Resposta muito clara e completa!"
  },
  {
    "timestamp": "2025-06-04T15:00:00.000000",
    "question": "Quais são os orixás?",
    "answer": "Os orixás são entidades...",
    "rating": 4,
    "comment": null
  }
]
```

**Campos:**
- `timestamp`: Data/hora UTC no formato ISO 8601
- `question`: Pergunta feita pelo usuário
- `answer`: Resposta gerada pelo sistema
- `rating`: Avaliação de 1 a 5 estrelas
- `comment`: Comentário opcional do usuário

### Frontend

#### Componente RatingWidget (`frontend/src/components/RatingWidget.tsx`)

**Props:**
```typescript
interface RatingWidgetProps {
  question: string;   // Pergunta atual
  answer: string;     // Resposta gerada
  onSubmit?: () => void; // Callback após envio (opcional)
}
```

**Funcionalidades:**
1. **Seleção de Estrelas:** Interação visual com hover e click
2. **Campo de Comentário:** Aparece após selecionar rating (máx 500 caracteres)
3. **Validação:** Requer pelo menos 1 estrela antes de enviar
4. **Feedback Visual:** Mensagem de sucesso após envio
5. **Estados:** Loading, submitted, error handling

**Estados Visuais:**
- Estrelas cinzas (não selecionadas)
- Estrelas amarelas (hover ou selecionadas)
- Contador de caracteres do comentário
- Botão desabilitado durante envio
- Mensagem de sucesso (verde) após envio

#### Integração com AnswerCard

O `RatingWidget` é renderizado automaticamente em `AnswerCard.tsx` após cada resposta:

```tsx
{question && (
  <RatingWidget question={question} answer={answer} />
)}
```

#### Fluxo de Estado no App.tsx

1. Usuário faz pergunta → `currentQuestion` é atualizada
2. Resposta é recebida → `AnswerCard` renderizado com `question` prop
3. `RatingWidget` é exibido automaticamente
4. Usuário avalia → Feedback enviado para backend
5. Sucesso → Mensagem de agradecimento exibida

## Uso

### Para Usuários

1. Faça uma pergunta no chat
2. Aguarde a resposta aparecer
3. Abaixo da resposta, clique nas estrelas (1-5)
4. Opcionalmente, adicione um comentário
5. Clique em "Enviar Avaliação"
6. Veja a mensagem de confirmação

### Para Desenvolvedores

#### Testar Localmente

1. **Backend em execução:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. **Frontend em execução:**
```bash
cd frontend
npm run dev
```

3. **Fazer pergunta e avaliar resposta**

4. **Verificar arquivo de feedbacks:**
```bash
cat backend/data/feedback.json
```

#### Testar Endpoint Diretamente

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Teste",
    "answer": "Resposta teste",
    "rating": 5,
    "comment": "Excelente!"
  }'
```

**Resposta esperada:**
```json
{"status":"success","message":"Feedback salvo com sucesso"}
```

## Análise de Feedbacks

### Métricas Úteis

1. **Rating Médio:** Qualidade geral das respostas
2. **Distribuição de Ratings:** Identificar padrões (muitos 1-2 vs 4-5)
3. **Comentários Negativos (1-2 ⭐):** Problemas específicos
4. **Perguntas Frequentes com Baixo Rating:** Tópicos que precisam melhorias
5. **Timestamps:** Horários de maior uso/satisfação

### Script Python para Análise (Exemplo)

```python
import json
from collections import Counter
from datetime import datetime

# Carregar feedbacks
with open('backend/data/feedback.json', 'r', encoding='utf-8') as f:
    feedbacks = json.load(f)

# Calcular rating médio
ratings = [fb['rating'] for fb in feedbacks]
avg_rating = sum(ratings) / len(ratings)
print(f"Rating Médio: {avg_rating:.2f} ⭐")

# Distribuição de ratings
dist = Counter(ratings)
print("\nDistribuição:")
for rating in sorted(dist.keys(), reverse=True):
    print(f"{rating} ⭐: {dist[rating]} ({dist[rating]/len(ratings)*100:.1f}%)")

# Feedbacks negativos (1-2 estrelas)
negative = [fb for fb in feedbacks if fb['rating'] <= 2]
print(f"\nFeedbacks Negativos: {len(negative)}")
for fb in negative:
    print(f"  Q: {fb['question'][:50]}...")
    if fb['comment']:
        print(f"  Comentário: {fb['comment']}")
```

## Próximos Passos

### v1.1.0 (Curto Prazo)
- [ ] Dashboard de análise de feedbacks no frontend
- [ ] Gráficos de tendência de ratings ao longo do tempo
- [ ] Exportar feedbacks para CSV/Excel
- [ ] Notificações para ratings baixos (<3 ⭐)

### v1.2.0 (Médio Prazo)
- [ ] Machine Learning: Identificar padrões em respostas bem avaliadas
- [ ] Fine-tuning de embeddings baseado em feedbacks
- [ ] A/B testing de diferentes prompts usando ratings como métrica
- [ ] Detecção automática de tópicos problemáticos

### v2.0.0 (Longo Prazo)
- [ ] Sistema de recompensa para usuários que dão feedbacks
- [ ] Integração com banco de dados (PostgreSQL)
- [ ] API analytics para visualização em BI tools
- [ ] Modelo de ML para prever qualidade de resposta antes de exibir

## Configuração de Ambiente

### Variáveis de Ambiente

O frontend usa `VITE_BACKEND_URL` para conectar ao endpoint:

**.env.local (desenvolvimento):**
```
VITE_BACKEND_URL=http://localhost:8000
```

**.env.production:**
```
VITE_BACKEND_URL=https://dev-mateus-backend-aiye.hf.space
```

### CORS

O backend já está configurado para aceitar requisições do frontend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://aiye-chat.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Segurança

### Considerações

1. **Rate Limiting:** Considerar implementar limite de feedbacks por IP/usuário
2. **Validação:** Pydantic valida todos os campos automaticamente
3. **Sanitização:** Comentários são limitados a 500 caracteres
4. **CORS:** Apenas domínios autorizados podem enviar feedbacks
5. **Armazenamento:** JSON é adequado para MVP, migrar para DB em produção

### Recomendações Futuras

- Implementar autenticação para rastrear usuários
- Adicionar captcha para prevenir spam
- Criptografar dados sensíveis (se houver)
- Backup automático de feedback.json
- Migrar para banco de dados relacional (PostgreSQL)

## Troubleshooting

### Problema: Feedback não está sendo salvo

**Possíveis causas:**
1. Permissões de escrita no diretório `backend/data/`
2. JSON malformado no arquivo existente
3. Disco cheio

**Solução:**
```bash
# Verificar permissões
ls -la backend/data/

# Criar diretório se não existir
mkdir -p backend/data/

# Verificar JSON
python -m json.tool backend/data/feedback.json

# Verificar espaço em disco
df -h
```

### Problema: Rating não aparece no frontend

**Possíveis causas:**
1. `question` não está sendo passada para `AnswerCard`
2. Componente `RatingWidget` não importado
3. Erro de compilação no TypeScript

**Solução:**
```bash
# Verificar console do navegador (F12)
# Verificar erros de compilação
npm run build

# Verificar importações
grep -r "RatingWidget" frontend/src/
```

### Problema: Endpoint /feedback retorna 500

**Possíveis causas:**
1. Modelo `FeedbackRequest` não importado em `main.py`
2. Erro ao criar diretório `data/`
3. JSON existente corrompido

**Solução:**
```python
# Testar import
python -c "from backend.models import FeedbackRequest; print('OK')"

# Verificar logs do backend
# Procurar por "✗ Erro ao salvar feedback"

# Resetar arquivo de feedbacks
echo "[]" > backend/data/feedback.json
```

## Contribuindo

Para adicionar novas funcionalidades ao sistema de feedback:

1. Atualizar modelo em `backend/models.py` se necessário
2. Modificar endpoint `/feedback` em `backend/main.py`
3. Atualizar componente `RatingWidget.tsx` para novos campos
4. Adicionar testes unitários
5. Atualizar esta documentação

## Referências

- **FastAPI Validation:** https://fastapi.tiangolo.com/tutorial/body-fields/
- **Pydantic Models:** https://docs.pydantic.dev/latest/concepts/models/
- **React Hooks:** https://react.dev/reference/react/hooks
- **TypeScript Types:** https://www.typescriptlang.org/docs/handbook/2/everyday-types.html
