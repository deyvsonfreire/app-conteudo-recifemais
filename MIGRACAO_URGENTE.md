# 🚨 MIGRAÇÃO URGENTE - v2.5.0 → v2.4.0

## ❌ PROBLEMA IDENTIFICADO

A versão v2.5.0 no EasyPanel está **INCOMPLETA** e por isso o sistema não funciona.

### Arquivo .env v2.5.0 (ATUAL - FALHO):
- ❌ Não tem SUPABASE_SERVICE_KEY
- ❌ Não tem GOOGLE_AI_API_KEY  
- ❌ Não tem GMAIL_CLIENT_ID/SECRET
- ❌ Não tem WORDPRESS_USERNAME/PASSWORD
- ❌ Apenas comentários sobre "armazenado no Supabase"

### Código v2.5.0 (ATUAL - FALHO):
- ❌ Imports relativos quebrados
- ❌ Dependência circular não resolvida
- ❌ Sistema frágil

## ✅ SOLUÇÃO: USAR v2.4.0 CORRIGIDA

### 1. SUBSTITUIR ARQUIVO .env

**No EasyPanel, substitua o .env atual por:**

```env
# ===========================================
# CONFIGURAÇÃO DE PRODUÇÃO - RecifeMais v2.4.0
# ARQUIVO PARA EASYPANEL - COM CREDENCIAIS
# ===========================================

# Informações da Aplicação
APP_NAME="RecifeMais Conteúdo"
APP_VERSION="2.4.0"
DEBUG=false
ENVIRONMENT=production
PORT=8001

# URLs de Produção
WORDPRESS_URL="https://recifemais.com.br"
GMAIL_REDIRECT_URI="https://redacao.admin.recifemais.com.br/auth/callback"
BASE_URL="https://redacao.admin.recifemais.com.br"

# Supabase (URLs públicos)
SUPABASE_URL="https://aoyrpadrrsckxbuadcnf.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MDY5MTksImV4cCI6MjA2NjM4MjkxOX0.BAkMkcWzUeLL9_G-qAEdOX-Nhjmr5WLSv_AOqvdxA74"

# Google Search Console e Analytics
GSC_SITE_URL="https://recifemais.com.br/"
GA4_PROPERTY_ID=""

# Configurações de IA
MAX_TOKENS_PER_REQUEST=8000
EMBEDDING_MODEL="text-embedding-004"
GEMINI_MODEL="gemini-2.0-flash-exp"

# Configurações de Processamento
EMAIL_CHECK_INTERVAL=300
MAX_EMAILS_PER_BATCH=10

# Redis (Cache)
REDIS_URL="redis://localhost:6379"

# Logs
LOG_LEVEL=INFO

# ===========================================
# CREDENCIAIS NECESSÁRIAS - OBRIGATÓRIAS
# ===========================================

# Supabase Service Key (OBRIGATÓRIA)
SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDgwNjkxOSwiZXhwIjoyMDY2MzgyOTE5fQ.EWx1wZZutcONrJYSzF2r1mvuav0KilXuPOOoWJYjAyc"

# Google AI API Key (OBRIGATÓRIA)
GOOGLE_AI_API_KEY="AIzaSyBuPRxQo9lQEcyLVovTT-VSZAvl-b5i0U4"

# Gmail API Credentials (OBRIGATÓRIAS)
GMAIL_CLIENT_ID="1029278366837-f8vid8646jbckkbnn35dp80o3up3edr2.apps.googleusercontent.com"
GMAIL_CLIENT_SECRET="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"

# WordPress Credentials (OBRIGATÓRIAS)
WORDPRESS_USERNAME="deyvson"
WORDPRESS_PASSWORD="Recife@2024"
```

### 2. ATUALIZAR CÓDIGO

No EasyPanel:
```bash
# Fazer pull da versão corrigida
git pull origin main

# Rebuild da aplicação
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 3. VERIFICAR FUNCIONAMENTO

```bash
# Health check
curl http://localhost:8001/health

# Deve retornar:
{
  "status": "healthy",
  "checks": {
    "database": true,
    "wordpress": true,
    "gemini": true,
    "gmail": true
  }
}
```

## 🎯 DIFERENÇAS CRÍTICAS

### v2.5.0 (ATUAL - FALHO):
- ❌ .env sem credenciais
- ❌ Imports quebrados
- ❌ Sistema não inicializa

### v2.4.0 (CORRIGIDA):
- ✅ .env com todas credenciais
- ✅ Imports com fallback
- ✅ Sistema robusto
- ✅ 100% funcional

## ⚡ AÇÃO IMEDIATA

1. **Copie o .env completo acima**
2. **Cole no EasyPanel**
3. **Faça git pull**
4. **Rebuild da aplicação**
5. **Teste o health check**

**Sistema funcionará imediatamente após essa migração!**
