# Guia de Setup: PostgreSQL com Neon

## ✅ Implementação Completa

O sistema agora usa **PostgreSQL (Neon)** para armazenar feedbacks de forma persistente e escalável.

## 🚀 Setup Rápido (5 minutos)

### Passo 1: Criar Conta no Neon

1. Acesse: **https://neon.tech**
2. Clique em **"Sign Up"** (pode usar GitHub)
3. Confirme o email

### Passo 2: Criar Projeto

1. No dashboard, clique em **"Create a project"**
2. **Name:** `aiye-feedbacks`
3. **Region:** US East (Ohio) - us-east-2 (mais próximo do Brasil)
4. **PostgreSQL version:** 16 (padrão)
5. Clique em **"Create Project"**

### Passo 3: Copiar Connection String

Após criar o projeto, você verá uma tela com:

```
Connection string
postgresql://neondb_owner:AbC123XyZ@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**Copie essa string completa!**

### Passo 4: Configurar Variáveis de Ambiente

#### Localmente (.env na raiz do projeto):

```bash
# Adicione ao arquivo .env
DATABASE_URL=postgresql://neondb_owner:AbC123XyZ@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

#### Hugging Face Spaces:

1. Acesse: https://huggingface.co/spaces/dev-mateus/backend-aiye/settings
2. Vá em **"Repository secrets"**
3. Clique em **"Add a secret"**
4. **Name:** `DATABASE_URL`
5. **Value:** cole a connection string do Neon
6. Clique em **"Add secret"**

#### Vercel (Frontend - opcional):

Se quiser criar uma página admin no frontend:

1. Acesse: https://vercel.com/dashboard
2. Vá no projeto `aiye-chat`
3. **Settings** → **Environment Variables**
4. **Name:** `DATABASE_URL`
5. **Value:** cole a connection string
6. **Save**

### Passo 5: Instalar Dependências

```bash
cd backend
pip install psycopg2-binary==2.9.9
```

Ou reinstale tudo:

```bash
pip install -r requirements.txt
```

### Passo 6: Testar Localmente

```bash
# Iniciar backend
python run_backend.py
```

Você deve ver:
```
✓ Tabela de feedbacks criada/verificada com sucesso
✓ Banco de dados inicializado
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Passo 7: Testar Endpoint

```powershell
# Enviar feedback
curl.exe -X POST http://localhost:8000/feedback `
  -H "Content-Type: application/json" `
  -d '{\"question\":\"Teste PostgreSQL\",\"answer\":\"Funciona!\",\"rating\":5,\"comment\":\"Persistente agora!\"}'
```

**Resposta esperada:**
```json
{
  "status": "success",
  "message": "Feedback salvo com sucesso",
  "id": 1
}
```

```powershell
# Listar feedbacks
curl.exe http://localhost:8000/feedbacks
```

**Resposta esperada:**
```json
{
  "total": 1,
  "avg_rating": 5.0,
  "positive": 1,
  "negative": 0,
  "feedbacks": [
    {
      "id": 1,
      "timestamp": "2025-11-26T15:30:00",
      "question": "Teste PostgreSQL",
      "answer": "Funciona!",
      "rating": 5,
      "comment": "Persistente agora!"
    }
  ],
  "pagination": {
    "limit": 100,
    "offset": 0
  }
}
```

## 📊 Estrutura do Banco de Dados

### Tabela: `feedbacks`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | SERIAL | ID único (auto-incremento) |
| `timestamp` | TIMESTAMP | Data/hora do feedback |
| `question` | TEXT | Pergunta feita pelo usuário |
| `answer` | TEXT | Resposta gerada pelo sistema |
| `rating` | INTEGER | Avaliação (1-5 estrelas) |
| `comment` | TEXT | Comentário opcional |
| `created_at` | TIMESTAMP | Data de criação do registro |

**Índices:**
- `idx_feedbacks_timestamp` - Acelera ordenação por data
- `idx_feedbacks_rating` - Acelera filtros por rating

**Constraints:**
- `rating >= 1 AND rating <= 5` - Garante ratings válidos

## 🔍 Consultas Úteis

### Via SQL (Console do Neon)

Acesse: https://console.neon.tech → Seu projeto → SQL Editor

```sql
-- Ver todos os feedbacks
SELECT * FROM feedbacks ORDER BY timestamp DESC LIMIT 10;

-- Estatísticas
SELECT 
  COUNT(*) as total,
  AVG(rating) as media,
  COUNT(CASE WHEN rating >= 4 THEN 1 END) as positivos,
  COUNT(CASE WHEN rating <= 2 THEN 1 END) as negativos
FROM feedbacks;

-- Feedbacks negativos (para análise)
SELECT question, answer, rating, comment 
FROM feedbacks 
WHERE rating <= 2 
ORDER BY timestamp DESC;

-- Top perguntas mais avaliadas
SELECT question, COUNT(*) as total_avaliacoes, AVG(rating) as media
FROM feedbacks
GROUP BY question
HAVING COUNT(*) > 1
ORDER BY total_avaliacoes DESC;
```

### Via API

```powershell
# Listar com paginação
curl.exe "http://localhost:8000/feedbacks?limit=10&offset=0"

# Próxima página
curl.exe "http://localhost:8000/feedbacks?limit=10&offset=10"
```

## ✅ Vantagens dessa Implementação

1. **Persistente**: Dados nunca são perdidos (mesmo com rebuild do HF Spaces)
2. **Rápido**: Queries otimizadas com índices
3. **Escalável**: Suporta milhões de registros
4. **Gratuito**: Neon tier gratuito: 0.5 GB storage, compute ilimitado
5. **Seguro**: Connection string com SSL, senha criptografada
6. **Paginação**: API retorna dados em lotes (evita sobrecarga)
7. **Estatísticas**: Média, positivos, negativos calculados automaticamente

## 🔧 Troubleshooting

### Erro: "psycopg2 not found"

```bash
pip install psycopg2-binary==2.9.9
```

### Erro: "could not connect to server"

1. Verifique se `DATABASE_URL` está definida corretamente
2. Teste a connection string no console do Neon
3. Verifique se há firewall bloqueando porta 5432

### Erro: "relation 'feedbacks' does not exist"

A tabela será criada automaticamente na primeira inicialização. Se não for:

1. Acesse o SQL Editor do Neon
2. Execute:
```sql
CREATE TABLE feedbacks (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Verificar Logs do HF Spaces

1. Acesse: https://huggingface.co/spaces/dev-mateus/backend-aiye
2. Clique em **"Logs"**
3. Procure por:
   - `✓ Tabela de feedbacks criada/verificada com sucesso`
   - `✓ Banco de dados inicializado`
   - `✓ Feedback recebido: 5 estrelas (ID: 1)`

## 📈 Monitoramento (Neon Dashboard)

1. Acesse: https://console.neon.tech
2. Selecione o projeto `aiye-feedbacks`
3. Veja:
   - **Storage**: Quanto espaço está sendo usado
   - **Compute**: Tempo de CPU usado
   - **Connections**: Conexões ativas
   - **Queries**: Queries executadas

## 🚀 Deploy

### Commit e Push

```bash
git add .
git commit -m "feat: migrar feedbacks para PostgreSQL (Neon)"
git push origin main
git push space main
```

### Configurar no HF Spaces

⚠️ **IMPORTANTE**: Adicione `DATABASE_URL` nos secrets do HF Spaces ANTES de fazer push!

Caso contrário, o backend vai iniciar mas não vai salvar feedbacks.

## 📝 Próximos Passos

- [ ] Adicionar autenticação ao endpoint `/feedbacks` (apenas admin)
- [ ] Criar dashboard visual no frontend
- [ ] Adicionar filtros (por rating, data, etc)
- [ ] Exportar feedbacks para CSV
- [ ] Notificações para feedbacks negativos (< 3 estrelas)
- [ ] Análise de sentimento nos comentários
