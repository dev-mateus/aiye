# 🚨 Resposta ao Incidente de Segurança - PostgreSQL URI Exposta

**Data do Incidente**: 28 de novembro de 2025  
**Severidade**: 🔴 CRÍTICA  
**Status**: ⚠️ EM REMEDIAÇÃO

---

## 📋 Resumo do Incidente

GitGuardian detectou **PostgreSQL URI exposta** no repositório público `dev-mateus/aiye` no GitHub.

**Credencial exposta**:
- Tipo: PostgreSQL Connection String (Neon)
- Primeiro commit: 17 de novembro de 2025 (commit `f451dbb`)
- Exposição: Repositório tornou-se público posteriormente
- Duração da exposição: ~11 dias

---

## 🔍 Análise de Impacto

### Arquivos Afetados

1. **`HF_SPACES_SECRET.md`** (commit f451dbb - 26/11/2025)
   - Continha: DATABASE_URL completa como exemplo
   - Risco: ALTO - arquivo de documentação, fácil de encontrar

2. **`check_db_size.py`** (commit e8f4df1 - 17/11/2025)
   - Continha: DATABASE_URL como fallback
   - Risco: ALTO - código de utilidade

3. **`test_db_connection.py`** (commit e8f4df1 - 17/11/2025)
   - Continha: 3 variações da DATABASE_URL
   - Risco: CRÍTICO - múltiplas exposições

### Dados Sensíveis Expostos

```
Host: ep-polished-truth-ae0kk3zf.c-2.us-east-2.aws.neon.tech
Database: neondb
User: neondb_owner
Password: npg_CHtQo6Uk9LEa
```

⚠️ **Esta credencial está COMPROMETIDA e deve ser rotacionada IMEDIATAMENTE!**

---

## ✅ Ações Já Executadas

1. **Remediação de Código** ✅
   - [x] Removida DATABASE_URL de `HF_SPACES_SECRET.md`
   - [x] Removida DATABASE_URL de `check_db_size.py`
   - [x] Removida DATABASE_URL de `test_db_connection.py`
   - [x] Adicionada validação obrigatória de env var
   - [x] Commit de segurança criado

2. **Documentação** ✅
   - [x] Atualizado `SECURITY.md` com registro do incidente
   - [x] Criado este guia de resposta ao incidente

---

## 🔧 Ações URGENTES Necessárias

### 1. ⚠️ ROTACIONAR CREDENCIAL DO NEON (PRIORITÁRIO)

**Por que é urgente?**
A credencial está no histórico público do Git. Mesmo removendo dos arquivos atuais, ela permanece acessível em commits antigos.

**Como fazer:**

1. **Acesse Neon Console**: https://console.neon.tech

2. **Opção A - Resetar Senha do Usuário** (Mais Rápido)
   - Vá para seu projeto
   - Settings > Users
   - Selecione `neondb_owner`
   - Clique em "Reset Password"
   - Copie a nova senha
   - Atualize `DATABASE_URL` em todos os lugares:
     - `.env` local
     - HuggingFace Spaces Secrets
     - Vercel Environment Variables (se aplicável)

3. **Opção B - Criar Novo Usuário** (Mais Seguro)
   - Settings > Users > Create User
   - Nome: `aiye_production`
   - Gere senha forte
   - Grant role: `neondb_owner` ou crie role específica
   - Revogue acesso do usuário antigo
   - Atualize DATABASE_URL com novo usuário

4. **Opção C - Criar Novo Banco** (Mais Seguro, Mais Trabalhoso)
   - Create New Project
   - Migre dados se necessário
   - Delete projeto antigo
   - Atualize toda configuração

**Recomendação**: Opção B (criar novo usuário e revogar antigo)

### 2. 🧹 LIMPAR HISTÓRICO DO GIT (OPCIONAL MAS RECOMENDADO)

A credencial ainda existe no histórico do Git, mesmo após remover dos arquivos.

**Opção A: BFG Repo-Cleaner** (Mais Simples)

```powershell
# 1. Instalar BFG
# Baixe de: https://rtyley.github.io/bfg-repo-cleaner/

# 2. Clone mirror do repositório
git clone --mirror https://github.com/dev-mateus/aiye.git

# 3. Criar arquivo com a senha a ser removida
echo "npg_CHtQo6Uk9LEa" > passwords.txt

# 4. Executar BFG
java -jar bfg.jar --replace-text passwords.txt aiye.git

# 5. Expirar reflog e garbage collect
cd aiye.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 6. Force push
git push --force
```

**Opção B: git-filter-repo** (Mais Controle)

```powershell
# 1. Instalar git-filter-repo
pip install git-filter-repo

# 2. Criar arquivo de substituições
# substitutions.txt:
regex:npg_CHtQo6Uk9LEa==>***CREDENTIAL_REMOVED***
regex:ep-polished-truth-ae0kk3zf.c-2.us-east-2.aws.neon.tech==>***HOST_REMOVED***

# 3. Executar filter-repo
git filter-repo --replace-text substitutions.txt

# 4. Force push
git push --force --all
git push --force --tags
```

⚠️ **ATENÇÃO**: Force push reescreve histórico! Coordene com colaboradores.

### 3. 🔐 REVOGAR ACESSO VIA NEON CONSOLE

Mesmo após rotacionar, revogue explicitamente:

1. Neon Console > Settings > Security
2. Revoke/Delete credencial comprometida
3. Audite logs de acesso para detectar uso não autorizado

### 4. 📊 AUDITORIA DE LOGS

Verifique se houve acesso não autorizado:

1. **Neon Console > Monitoring**
   - Verifique conexões suspeitas
   - Horários fora do padrão
   - IPs desconhecidos

2. **Logs da aplicação**
   - Procure por queries maliciosas
   - Verificar tentativas de dump de dados

---

## 🛡️ Prevenção Futura

### 1. Pre-commit Hooks

Instale `gitleaks` para detectar segredos antes do commit:

```powershell
# Instalar gitleaks
# https://github.com/gitleaks/gitleaks/releases

# Adicionar pre-commit hook
# .git/hooks/pre-commit
gitleaks protect --verbose --redact --staged
```

### 2. GitHub Secret Scanning

GitHub já detecta alguns tipos de secrets. Para Neon:

1. Settings > Code security and analysis
2. Enable: Secret scanning
3. Enable: Push protection

### 3. Revisão de Código

Antes de commitar:
- ✅ Nunca commitar valores reais em `.env.example`
- ✅ Sempre usar variáveis de ambiente
- ✅ Revisar diff antes do push
- ✅ Usar placeholders em documentação

### 4. Rotação Regular

Implemente política de rotação:
- Credenciais de banco: a cada 90 dias
- API keys: a cada 180 dias
- Senhas admin: a cada 30 dias

---

## 📞 Contatos de Emergência

- **Neon Support**: https://neon.tech/docs/introduction/support
- **GitHub Security**: https://github.com/security/advisories
- **GitGuardian**: support@gitguardian.com

---

## 📝 Checklist de Remediação

### Imediato (Hoje)
- [ ] Rotacionar credencial do Neon PostgreSQL
- [ ] Atualizar DATABASE_URL em .env local
- [ ] Atualizar DATABASE_URL no HuggingFace Spaces
- [ ] Testar aplicação após rotação
- [ ] Auditar logs do Neon para acessos suspeitos

### Curto Prazo (Esta Semana)
- [ ] Limpar histórico do Git com BFG ou git-filter-repo
- [ ] Force push para GitHub
- [ ] Notificar colaboradores sobre force push
- [ ] Verificar que repositório GitHub continua privado
- [ ] Configurar GitHub Secret Scanning

### Médio Prazo (Este Mês)
- [ ] Implementar pre-commit hooks (gitleaks)
- [ ] Documentar processo de rotação de credenciais
- [ ] Criar política de segurança formal
- [ ] Treinar time sobre boas práticas

### Longo Prazo (Próximos 3 Meses)
- [ ] Implementar autenticação JWT no backend
- [ ] Adicionar rate limiting
- [ ] Implementar logs de auditoria
- [ ] Configurar alertas de segurança automatizados

---

## 📚 Lições Aprendidas

1. **Nunca** usar valores reais em arquivos de exemplo/documentação
2. **Sempre** usar placeholders como `your_password_here`
3. **Validar** ausência de secrets antes de tornar repo público
4. **Configurar** ferramentas de detecção antes do primeiro commit
5. **Revisar** histórico completo antes de tornar repo público

---

## ✅ Resolução

Este incidente será considerado **RESOLVIDO** quando:

1. ✅ Credencial rotacionada
2. ✅ DATABASE_URL atualizada em todos ambientes
3. ✅ Histórico do Git limpo (opcional mas recomendado)
4. ✅ Auditoria de logs concluída sem acessos suspeitos
5. ✅ Pre-commit hooks instalados
6. ✅ Política de rotação documentada

---

**Responsável**: dev-mateus  
**Última atualização**: 28 de novembro de 2025
