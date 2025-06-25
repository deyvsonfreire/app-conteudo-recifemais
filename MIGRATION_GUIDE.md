# 🔐 Guia de Migração para Credenciais Seguras

## 📋 **RESUMO DA MUDANÇA**

O sistema foi atualizado para armazenar credenciais sensíveis no banco de dados Supabase em vez de arquivos `.env`, aumentando significativamente a segurança e persistência.

## 🚀 **PASSOS PARA MIGRAÇÃO**

### **1. Fazer Deploy da Nova Versão**
```bash
# O código já foi enviado para GitHub
# Faça redeploy no EasyPanel para aplicar as mudanças
```

### **2. Migrar Credenciais Automaticamente**
```bash
# Endpoint para migração automática das credenciais
curl -X POST https://recmais-recifemais-conteudo.tmjyor.easypanel.host/admin/migrate-credentials
```

**Resposta esperada:**
```json
{
  "message": "Migração concluída: 6/6 credenciais",
  "success_count": 6,
  "total_count": 6,
  "results": [...]
}
```

### **3. Verificar Migração**
```bash
# Verificar se as credenciais foram migradas corretamente
curl https://recmais-recifemais-conteudo.tmjyor.easypanel.host/admin/secure-config
```

**Resposta esperada:**
```json
{
  "configs": [
    {"key": "wordpress_username", "defined": true, "masked_value": "****"},
    {"key": "wordpress_password", "defined": true, "masked_value": "****"},
    {"key": "gmail_client_id", "defined": true, "masked_value": "****"},
    {"key": "gmail_client_secret", "defined": true, "masked_value": "****"},
    {"key": "google_ai_api_key", "defined": true, "masked_value": "****"},
    {"key": "supabase_service_key", "defined": true, "masked_value": "****"}
  ]
}
```

### **4. Testar Funcionamento**
```bash
# Testar health check
curl https://recmais-recifemais-conteudo.tmjyor.easypanel.host/health

# Reautenticar Gmail (se necessário)
# Acesse: https://recmais-recifemais-conteudo.tmjyor.easypanel.host/auth/gmail/redirect
```

### **5. Atualizar Arquivo .env (APÓS CONFIRMAR FUNCIONAMENTO)**

Substitua o conteúdo do seu arquivo `.env` por:

```env
# =============================================================================
# CONFIGURAÇÕES RECIFEMAIS CONTEÚDO - VERSÃO SEGURA
# =============================================================================
# IMPORTANTE: Este arquivo NÃO contém credenciais sensíveis
# Credenciais sensíveis são armazenadas no banco de dados Supabase
# =============================================================================

# Configurações Gerais da Aplicação
APP_NAME=RecifeMais Conteúdo
APP_VERSION=2.2.1
DEBUG=false

# URLs e Endpoints Públicos
WORDPRESS_URL=https://v25.recifemais.com.br
GMAIL_REDIRECT_URI=https://recmais-recifemais-conteudo.tmjyor.easypanel.host/auth/callback

# Configurações Supabase (URLs públicos)
SUPABASE_URL=https://aoyrpadrrsckxbuadcnf.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MDY5MTksImV4cCI6MjA2NjM4MjkxOX0.BAkMkcWzUeLL9_G-qAEdOX-Nhjmr5WLSv_AOqvdxA74

# Cache Redis (Desenvolvimento)
REDIS_URL=redis://localhost:6379

# Configurações de IA
MAX_TOKENS_PER_REQUEST=8000
EMBEDDING_MODEL=text-embedding-004
GEMINI_MODEL=gemini-2.0-flash-exp

# Configurações de Processamento
EMAIL_CHECK_INTERVAL=300
MAX_EMAILS_PER_BATCH=10

# =============================================================================
# CREDENCIAIS SENSÍVEIS - AGORA ARMAZENADAS NO BANCO DE DADOS
# =============================================================================
# As seguintes credenciais foram migradas para o banco de dados Supabase:
# - WORDPRESS_USERNAME (wordpress_username)
# - WORDPRESS_PASSWORD (wordpress_password) 
# - GMAIL_CLIENT_ID (gmail_client_id)
# - GMAIL_CLIENT_SECRET (gmail_client_secret)
# - GOOGLE_AI_API_KEY (google_ai_api_key)
# - SUPABASE_SERVICE_KEY (supabase_service_key)
#
# Para gerenciar essas credenciais, use:
# GET /admin/secure-config - Listar configurações
# POST /admin/secure-config/{key} - Definir configuração
# POST /admin/migrate-credentials - Migrar do .env
# =============================================================================
```

## 🛡️ **BENEFÍCIOS DA MIGRAÇÃO**

1. **Segurança Avançada**: Credenciais protegidas com RLS no Supabase
2. **Persistência Total**: Gmail OAuth nunca mais perde conexão
3. **Zero Downtime**: Sistema continua funcionando durante redeploys
4. **Auditoria**: Histórico de atualizações de credenciais
5. **Performance**: Cache inteligente para configurações
6. **Flexibilidade**: Gerenciamento via API

## 🔧 **GERENCIAMENTO DE CREDENCIAIS**

### **Listar Configurações:**
```bash
GET /admin/secure-config
```

### **Definir/Atualizar Credencial:**
```bash
POST /admin/secure-config/{key}
Content-Type: application/x-www-form-urlencoded

value=nova_credencial&description=Descrição opcional
```

### **Exemplo - Atualizar senha WordPress:**
```bash
curl -X POST \
  https://recmais-recifemais-conteudo.tmjyor.easypanel.host/admin/secure-config/wordpress_password \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "value=nova_senha_wordpress&description=Senha atualizada em $(date)"
```

## 🚨 **IMPORTANTE**

- **NÃO remova** as credenciais do `.env` até confirmar que a migração funcionou
- **Teste todos os endpoints** após a migração
- **Mantenha backup** das credenciais em local seguro
- **Reautentique o Gmail** após o deploy

## 📞 **SUPORTE**

Se houver algum problema durante a migração:

1. Verifique os logs da aplicação
2. Confirme se a tabela `secure_config` foi criada no Supabase
3. Teste os endpoints de configuração
4. Entre em contato para suporte técnico 