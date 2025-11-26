# Guia Rápido: Testar Sistema de Avaliação

## 🔧 Problema Resolvido

O erro "Erro ao enviar feedback. Tente novamente." foi causado por:
- ❌ RatingWidget estava usando `VITE_BACKEND_URL` (incorreto)
- ✅ Corrigido para `VITE_API_BASE` (padrão do projeto)

**Commit:** `95ce42f` - fix: corrigir variável de ambiente no RatingWidget

## 🚀 Como Testar Agora

### Passo 1: Iniciar Backend

Abra um terminal PowerShell e execute:

```powershell
cd C:\Users\mateus\Documents\Projetos\aiye

# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1

# Iniciar backend
python run_backend.py
```

**Saída esperada:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Passo 2: Iniciar Frontend

Abra **OUTRO** terminal PowerShell e execute:

```powershell
cd C:\Users\mateus\Documents\Projetos\aiye\frontend

# Instalar dependências (se ainda não fez)
npm install

# Iniciar frontend
npm run dev
```

**Saída esperada:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Passo 3: Testar no Navegador

1. Abra: http://localhost:5173/
2. **Faça uma pergunta**, exemplo: "O que é Umbanda?"
3. **Aguarde a resposta** aparecer
4. **Abaixo da resposta**, você verá: "Esta resposta foi útil?"
5. **Clique em 3-5 estrelas** ⭐⭐⭐⭐⭐
6. **(Opcional)** Digite um comentário
7. **Clique em "Enviar Avaliação"**
8. **Mensagem de sucesso:** "✓ Obrigado pela sua avaliação! Seu feedback nos ajuda a melhorar."

### Passo 4: Verificar Feedback Salvo

No terminal do backend, você deve ver:

```
✓ Feedback recebido: 5 estrelas
INFO:     127.0.0.1:xxxxx - "POST /feedback HTTP/1.1" 200 OK
```

**Verificar arquivo de feedbacks:**

```powershell
# Ver conteúdo do arquivo JSON
Get-Content backend\data\feedback.json | ConvertFrom-Json | Format-List
```

**Exemplo de saída:**

```
timestamp : 2025-11-26T14:30:00.000000
question  : O que é Umbanda?
answer    : Umbanda é uma religião brasileira...
rating    : 5
comment   : Resposta muito clara!
```

## 🐛 Se Ainda Houver Erro

### Console do Navegador (F12)

Pressione **F12** no navegador e vá para a aba **Console**. Procure por:

```
Erro ao enviar feedback: [detalhes do erro]
```

### Possíveis Erros e Soluções

#### Erro: "Failed to fetch"
**Causa:** Backend não está rodando ou URL incorreta

**Solução:**
```powershell
# Testar se backend está respondendo
curl http://localhost:8000/healthz
# Deve retornar: {"status":"ok"}
```

#### Erro: CORS (Cross-Origin Resource Sharing)
**Causa:** Frontend tentando acessar backend de origem diferente

**Solução:** Já está configurado no backend para aceitar `localhost:5173`

#### Erro 422: Unprocessable Entity
**Causa:** Dados enviados estão fora do formato esperado

**Solução:** Verificar se rating está entre 1-5 (já validado no frontend)

#### Erro 500: Internal Server Error
**Causa:** Erro ao salvar arquivo JSON

**Solução:**
```powershell
# Criar diretório se não existir
New-Item -ItemType Directory -Force -Path backend\data

# Criar arquivo vazio
Set-Content backend\data\feedback.json -Value "[]"
```

## 📊 Testar Endpoint Diretamente (Opcional)

Se quiser testar o backend sem o frontend:

```powershell
# Usando curl.exe (Windows)
curl.exe -X POST http://localhost:8000/feedback `
  -H "Content-Type: application/json" `
  -d '{\"question\":\"Teste\",\"answer\":\"Resposta teste\",\"rating\":5,\"comment\":\"Excelente!\"}'
```

**Resposta esperada:**
```json
{"status":"success","message":"Feedback salvo com sucesso"}
```

## ✅ Checklist de Teste

- [ ] Backend rodando em http://localhost:8000
- [ ] Frontend rodando em http://localhost:5173
- [ ] Pergunta feita e resposta recebida
- [ ] Widget de avaliação aparece abaixo da resposta
- [ ] Estrelas são clicáveis e mudam de cor (cinza → amarelo)
- [ ] Contador "X de 5" aparece ao selecionar estrelas
- [ ] Campo de comentário aparece após selecionar rating
- [ ] Botão "Enviar Avaliação" está habilitado
- [ ] Ao clicar, mensagem verde de sucesso aparece
- [ ] Log "✓ Feedback recebido: X estrelas" aparece no terminal do backend
- [ ] Arquivo `backend/data/feedback.json` foi criado/atualizado

## 📝 Exemplo de Teste Completo

### Teste 1: Avaliação Positiva (5 ⭐)
1. Pergunta: "Quais são os orixás da Umbanda?"
2. Rating: 5 estrelas
3. Comentário: "Explicação muito completa e didática!"
4. Resultado esperado: ✅ Sucesso

### Teste 2: Avaliação Média (3 ⭐)
1. Pergunta: "O que é uma gira?"
2. Rating: 3 estrelas
3. Comentário: "Resposta correta mas poderia ter mais detalhes"
4. Resultado esperado: ✅ Sucesso

### Teste 3: Avaliação Negativa (1 ⭐)
1. Pergunta: "Como fazer oferenda?"
2. Rating: 1 estrela
3. Comentário: "Resposta muito superficial e genérica"
4. Resultado esperado: ✅ Sucesso

### Teste 4: Sem Comentário
1. Pergunta: "O que é um terreiro?"
2. Rating: 4 estrelas
3. Comentário: (deixar vazio)
4. Resultado esperado: ✅ Sucesso (comment: null no JSON)

## 🎯 Próximos Passos

Após testar localmente com sucesso:

1. **Fazer commit das alterações** (se houver)
2. **Deploy no Vercel** (frontend já está configurado)
3. **Testar em produção:** https://aiye-chat.vercel.app
4. **Monitorar feedbacks** em `backend/data/feedback.json`
5. **Analisar dados** usando scripts Python (ver FEEDBACK_SYSTEM.md)

## 📚 Documentação Completa

Para mais detalhes sobre arquitetura, análise de dados e troubleshooting avançado, consulte:

- **FEEDBACK_SYSTEM.md** - Documentação completa do sistema
- **QUICKSTART.md** - Guia geral do projeto
- **README.md** - Visão geral e deploy

## 💡 Dicas

- Use **Ctrl+Shift+I** (F12) para abrir DevTools e ver requisições HTTP
- Na aba **Network**, filtre por "feedback" para ver a requisição POST
- Console mostra erros detalhados se houver problemas
- Arquivo JSON é criado automaticamente na primeira avaliação
- Cada feedback adiciona uma entrada no array JSON
