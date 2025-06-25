# 🚀 Deploy RecifeMais Conteúdo no EasyPanel

## ⚡ Deploy Rápido (5 minutos)

### 1. 📁 **Upload do Projeto**
- Acesse seu EasyPanel
- Crie novo projeto: **"RecifeMais Conteúdo"**
- Upload todos os arquivos do projeto

### 2. ⚙️ **Configuração do Container**
```bash
# Porta
PORT: 8001

# Comando de inicialização
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001

# Dockerfile
Usar Dockerfile existente na raiz do projeto
```

### 3. 🌐 **Variáveis de Ambiente**
Copie e cole estas variáveis no EasyPanel:

```env
APP_NAME=RecifeMais Conteúdo
APP_VERSION=2.5.0
DEBUG=false
ENVIRONMENT=production
PORT=8001

WORDPRESS_URL=https://recifemais.com.br
BASE_URL=https://SEU-DOMINIO.easypanel.host
GMAIL_REDIRECT_URI=https://SEU-DOMINIO.easypanel.host/auth/callback

SUPABASE_URL=https://aoyrpadrrsckxbuadcnf.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MDY5MTksImV4cCI6MjA2NjM4MjkxOX0.BAkMkcWzUeLL9_G-qAEdOX-Nhjmr5WLSv_AOqvdxA74
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDgwNjkxOSwiZXhwIjoyMDY2MzgyOTE5fQ.EWx1wZZutcONrJYSzF2r1mvuav0KilXuPOOoWJYjAyc

MAX_TOKENS_PER_REQUEST=8000
EMBEDDING_MODEL=text-embedding-004
GEMINI_MODEL=gemini-2.0-flash-exp
EMAIL_CHECK_INTERVAL=300
MAX_EMAILS_PER_BATCH=10
LOG_LEVEL=INFO

# Credenciais (serão migradas automaticamente para o banco)
WORDPRESS_USERNAME=deyvson
WORDPRESS_PASSWORD=Recife@2024
GOOGLE_AI_API_KEY=AIzaSyBuPRxQo9lQEcyLVovTT-VSZAvl-b5i0U4
GMAIL_CLIENT_ID=1029278366837-f8vid8646jbckkbnn35dp80o3up3edr2.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=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
GSC_SITE_URL=https://recifemais.com.br/
GA4_PROPERTY_ID=396664273
```

**⚠️ IMPORTANTE:** Substitua `SEU-DOMINIO.easypanel.host` pelo seu domínio real!

### 4. 🚀 **Deploy**
- Clique em **"Deploy"**
- Aguarde 2-3 minutos para build e inicialização

## ✅ **Verificação Pós-Deploy**

### 1. 🏥 **Health Check**
Acesse: `https://seu-dominio.easypanel.host/health/dashboard`

Deve mostrar:
```json
{
  "status": "healthy",
  "checks": {
    "database": true,
    "auth": true,
    "wordpress": true,
    "gemini": true,
    "gmail": false,
    "google_data": false
  }
}
```

### 2. 🔄 **Migração Automática**
Acesse: `https://seu-dominio.easypanel.host/admin/migrate-credentials`

Isso vai:
- ✅ Migrar credenciais do .env para o banco
- ✅ Configurar sistema de segurança
- ✅ Preparar OAuth

### 3. 🔐 **Configuração OAuth Google**

#### Gmail:
1. Acesse: `https://seu-dominio.easypanel.host/auth/gmail`
2. Clique em **"Autorizar Gmail"**
3. Complete o processo OAuth

#### Google Analytics & Search Console:
1. Acesse: `https://seu-dominio.easypanel.host/auth/google`
2. Autorize as permissões necessárias

## 📊 **Interface Principal**

Após deploy completo, acesse:
- **Dashboard**: `https://seu-dominio.easypanel.host/`
- **API Docs**: `https://seu-dominio.easypanel.host/docs`
- **Admin**: `https://seu-dominio.easypanel.host/admin/secure-config`

## 🔧 **Configuração Google Console**

Para OAuth funcionar, adicione no Google Console:

### URIs de Redirecionamento Autorizados:
```
https://seu-dominio.easypanel.host/auth/callback
https://seu-dominio.easypanel.host/auth/gmail/callback
```

### Origens JavaScript Autorizadas:
```
https://seu-dominio.easypanel.host
```

## 🎯 **Testes Essenciais**

### 1. **Supabase** ✅
```bash
curl https://seu-dominio.easypanel.host/health
# Deve retornar: database: true
```

### 2. **WordPress** ✅
```bash
curl https://seu-dominio.easypanel.host/wordpress/posts
# Deve retornar lista de posts
```

### 3. **Gmail** (após OAuth)
```bash
curl https://seu-dominio.easypanel.host/gmail/status
# Deve retornar: authenticated: true
```

### 4. **Gemini AI** (após migração)
```bash
curl -X POST https://seu-dominio.easypanel.host/test-email
# Deve processar email de teste
```

## 🚨 **Troubleshooting**

### Problema: Container não inicia
**Solução**: Verifique logs no EasyPanel, geralmente é problema de variável de ambiente

### Problema: Database connection failed
**Solução**: Verifique SUPABASE_URL e SUPABASE_SERVICE_KEY

### Problema: OAuth não funciona
**Solução**: 
1. Verifique BASE_URL e GMAIL_REDIRECT_URI
2. Configure URIs no Google Console
3. Execute migração de credenciais

### Problema: Gemini API key invalid
**Solução**:
1. Acesse `/admin/migrate-credentials`
2. Ou configure manualmente em `/admin/secure-config`

## 📞 **Suporte**

Se algo não funcionar:
1. **Logs**: Verifique logs no EasyPanel
2. **Health**: Acesse `/health/dashboard`
3. **Diagnostic**: Acesse `/admin/system-diagnostic-complete`

## 🎉 **Deploy Concluído!**

Após seguir estes passos, você terá:
- ✅ Sistema funcionando online
- ✅ Todas as integrações configuradas
- ✅ OAuth Google funcionando
- ✅ Interface web acessível
- ✅ API documentada disponível

**Tempo total estimado: 5-10 minutos** 