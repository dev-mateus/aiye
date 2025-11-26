# ⚠️ CONFIGURAR ANTES DO DEPLOY

## Hugging Face Spaces: Adicionar Secret DATABASE_URL

**IMPORTANTE:** O backend não funcionará sem esta configuração!

### Passo a Passo:

1. Acesse: https://huggingface.co/spaces/dev-mateus/backend-aiye/settings

2. Role até a seção **"Repository secrets"**

3. Clique em **"New secret"**

4. Preencha:
   - **Name:** `DATABASE_URL`
   - **Value:** `postgresql://***REDACTED***`

5. Clique em **"Add secret"**

6. O Space vai fazer rebuild automaticamente

### Verificar se funcionou:

Após o rebuild (2-3 minutos), acesse:

```
https://dev-mateus-backend-aiye.hf.space/feedbacks
```

Deve retornar:
```json
{
  "total": 0,
  "avg_rating": 0,
  "positive": 0,
  "negative": 0,
  "feedbacks": []
}
```

### Logs para Verificar:

Acesse os logs: https://huggingface.co/spaces/dev-mateus/backend-aiye

Procure por:
- `✓ Tabela de feedbacks criada/verificada com sucesso`
- `✓ Banco de dados inicializado`

Se aparecer erro:
- `⚠️ Erro ao inicializar banco: ...`

Significa que o DATABASE_URL não foi configurado ou está incorreto.
