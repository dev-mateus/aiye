# 🔒 Segurança do Projeto Aiye

## ⚠️ IMPORTANTE: Variáveis de Ambiente Obrigatórias

Este projeto usa variáveis de ambiente para proteger informações sensíveis. **NUNCA** commite senhas, tokens ou API keys diretamente no código.

---

## 📋 Checklist de Segurança

### ✅ Backend (HuggingFace Spaces)

**Secrets obrigatórios** (configurar em Settings > Repository Secrets):

1. **`GOOGLE_API_KEY`** 🔑
   - API Key do Google AI Studio
   - Obtida em: https://aistudio.google.com/app/apikey
   - **NUNCA** commitar no código

2. **`DATABASE_URL`** 🗄️
   - Connection string do PostgreSQL (Neon)
   - Formato: `postgresql://user:password@host.region.neon.tech/dbname?sslmode=require`
   - Obtida em: https://console.neon.tech
   - **NUNCA** commitar no código

### ✅ Frontend (Vercel)

**Environment Variables obrigatórias** (configurar em Settings > Environment Variables):

1. **`VITE_API_BASE`** 🌐
   - URL do backend (HuggingFace Spaces)
   - Exemplo: `https://dev-mateus-backend-aiye.hf.space`
   - **Público** (ok expor)

2. **`VITE_ADMIN_PASSWORD`** 🔐
   - Senha para acessar painel admin
   - **CRÍTICO**: Deve ser forte e única
   - Sugestão: Use gerador de senhas (mínimo 16 caracteres)
   - **NUNCA** commitar no código
   - **SEM VALOR PADRÃO** - app não inicia sem essa variável

---

## 🚨 Vulnerabilidades Corrigidas

### ❌ ANTES (INSEGURO)
```tsx
const ADMIN_PASSWORD = import.meta.env.VITE_ADMIN_PASSWORD || 'Aiye@2024#';
```
**Problema**: Senha hardcoded visível no HuggingFace Spaces público.

### ✅ DEPOIS (SEGURO)
```tsx
const ADMIN_PASSWORD = import.meta.env.VITE_ADMIN_PASSWORD;
if (!ADMIN_PASSWORD) {
  // Retorna erro informativo
}
```
**Solução**: Obriga configuração da variável de ambiente, sem fallback inseguro.

---

## 🔧 Como Configurar Localmente

1. **Copie o arquivo de exemplo**:
   ```bash
   cp .env.example .env
   ```

2. **Edite `.env` com suas credenciais**:
   ```env
   # Backend
   GOOGLE_API_KEY=SuaChaveRealAqui
   DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
   
   # Frontend
   VITE_API_BASE=http://localhost:8000
   VITE_ADMIN_PASSWORD=SenhaSuperSegura123!@#
   ```

3. **Verifique que `.env` está no `.gitignore`**:
   ```bash
   cat .gitignore | grep .env
   # Deve retornar: .env
   ```

---

## 🌐 Como Configurar em Produção

### Vercel (Frontend)

1. Acesse: **Settings** > **Environment Variables**
2. Adicione:
   - `VITE_API_BASE` = `https://seu-space.hf.space`
   - `VITE_ADMIN_PASSWORD` = `[senha forte aqui]`
3. Deploy automático aplicará as variáveis

### HuggingFace Spaces (Backend)

1. Acesse: **Settings** > **Repository Secrets**
2. Adicione:
   - `GOOGLE_API_KEY` = `[sua chave do AI Studio]`
   - `DATABASE_URL` = `[connection string do Neon]`
3. Redeploy o Space para aplicar

---

## 🛡️ Boas Práticas

### ✅ FAÇA:
- ✅ Use variáveis de ambiente para **TODAS** as credenciais
- ✅ Mantenha `.env` no `.gitignore`
- ✅ Use senhas fortes (16+ caracteres, letras, números, símbolos)
- ✅ Rotacione senhas periodicamente
- ✅ Use `.env.example` apenas com placeholders

### ❌ NÃO FAÇA:
- ❌ **NUNCA** commite `.env` ou credenciais reais
- ❌ **NUNCA** use senhas padrão (como `admin`, `123456`)
- ❌ **NUNCA** exponha API keys em logs ou mensagens de erro
- ❌ **NUNCA** use valores hardcoded como fallback de segurança
- ❌ **NUNCA** compartilhe credenciais por email ou chat

---

## 🔍 Auditoria de Segurança

**Última verificação**: 28 de novembro de 2025

**Status atual**:
- ✅ `.env` está no `.gitignore`
- ✅ Nenhuma credencial hardcoded no código
- ✅ Senha admin obrigatoriamente via env var
- ✅ API keys via env var
- ✅ Database URL via env var
- ⚠️ Endpoints admin públicos (proteção apenas no frontend)

**Recomendações futuras**:
1. Implementar autenticação JWT no backend
2. Adicionar rate limiting nos endpoints
3. Implementar RBAC (Role-Based Access Control)
4. Adicionar logs de auditoria para ações admin

---

## 📞 Reportar Vulnerabilidade

Se você encontrar uma vulnerabilidade de segurança, **NÃO** abra uma issue pública.

Entre em contato diretamente com o mantenedor:
- GitHub: [@dev-mateus](https://github.com/dev-mateus)

---

## 📚 Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [HuggingFace Secrets](https://huggingface.co/docs/hub/spaces-overview#managing-secrets)
- [Google AI Studio API Keys](https://aistudio.google.com/app/apikey)
