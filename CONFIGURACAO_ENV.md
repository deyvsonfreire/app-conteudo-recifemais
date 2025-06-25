# 🔧 Guia de Configuração - Variáveis de Ambiente

## 📋 Arquivos Criados

### 1. `config_updated.env` - Configuração Completa
- ✅ **Todas as variáveis** do sistema v2.4.0
- ✅ **Documentação detalhada** de cada seção
- ✅ **Feature flags** e configurações avançadas
- ✅ **Notas de segurança** e melhores práticas

### 2. `config.production.env` - Configuração Simplificada
- ✅ **Variáveis essenciais** para produção
- ✅ **Configuração mínima** necessária
- ✅ **Fácil de configurar** e manter

## 🚀 Configuração Rápida para Produção

### Passo 1: Copiar arquivo base
```bash
cp config.production.env .env
```

### Passo 2: Configurar variáveis obrigatórias

#### 🔐 **SEGURANÇA (OBRIGATÓRIO)**
```env
# Gere uma chave secreta única de 256 bits
SECRET_KEY=sua_chave_secreta_super_segura_aqui_256_bits_minimo
```

#### 📧 **Gmail OAuth (OBRIGATÓRIO para emails)**
```env
GMAIL_CLIENT_ID=seu_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=seu_client_secret
```

#### 📊 **Google Analytics (OPCIONAL)**
```env
GA4_PROPERTY_ID=123456789
```

## 🔧 Configuração Detalhada

### 1. Obter Gmail OAuth Credentials

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Crie ou selecione um projeto
3. Habilite Gmail API
4. Vá em **Credenciais** > **Criar Credenciais** > **ID do cliente OAuth 2.0**
5. Configure:
   - **Tipo**: Aplicação web
   - **URIs de redirecionamento**: `https://redacao.admin.recifemais.com.br/auth/google/callback`
6. Copie Client ID e Client Secret

### 2. Obter Google Analytics Property ID

1. Acesse [Google Analytics](https://analytics.google.com)
2. Selecione sua propriedade
3. Vá em **Admin** > **Informações da propriedade**
4. Copie o **ID da propriedade** (formato: 123456789)

### 3. Gerar Secret Key Segura

```bash
# Usando Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Usando OpenSSL
openssl rand -base64 32

# Usando Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

## 📝 Variáveis por Categoria

### 🔐 **Autenticação**
```env
SECRET_KEY=                    # Chave JWT (OBRIGATÓRIO)
ACCESS_TOKEN_EXPIRE_MINUTES=60 # Duração do token
ALGORITHM=HS256                # Algoritmo JWT
```

### 🗄️ **Banco de Dados**
```env
SUPABASE_URL=                  # URL do Supabase
SUPABASE_ANON_KEY=            # Chave anônima
SUPABASE_SERVICE_KEY=         # Chave de serviço
```

### 🌐 **APIs Google**
```env
GOOGLE_API_KEY=               # Chave da API Google (Gemini)
GMAIL_CLIENT_ID=              # OAuth Gmail
GMAIL_CLIENT_SECRET=          # OAuth Gmail
GSC_SITE_URL=                 # URL do site no Search Console
GA4_PROPERTY_ID=              # ID do Google Analytics
```

### 📰 **WordPress**
```env
WORDPRESS_URL=                # URL do WordPress
WORDPRESS_USERNAME=           # Usuário WordPress
WORDPRESS_PASSWORD=           # Senha WordPress
```

### ⚙️ **Sistema**
```env
ENVIRONMENT=production        # Ambiente (production/development)
DEBUG=False                   # Debug mode
BASE_URL=                     # URL base da aplicação
PORT=8000                     # Porta do servidor
```

## 🚨 Configurações Críticas de Segurança

### ⚠️ **NUNCA FAÇA:**
- ❌ Commitar arquivos `.env` com valores reais
- ❌ Usar `DEBUG=True` em produção
- ❌ Usar chaves fracas ou padrão
- ❌ Expor credentials em logs

### ✅ **SEMPRE FAÇA:**
- ✅ Use variáveis de ambiente do sistema
- ✅ Rotacione chaves regularmente
- ✅ Configure CORS adequadamente
- ✅ Monitore logs de acesso

## 🔄 Deploy e Aplicação

### Railway/Heroku
```bash
# Definir variáveis no painel web ou via CLI
railway variables set SECRET_KEY=sua_chave_aqui
railway variables set GMAIL_CLIENT_ID=seu_client_id

# Ou via arquivo
railway variables set --file .env
```

### Docker
```bash
# Usar arquivo env
docker run --env-file .env seu_app

# Ou variáveis individuais
docker run -e SECRET_KEY=sua_chave -e GMAIL_CLIENT_ID=seu_id seu_app
```

### Servidor Local
```bash
# Copiar arquivo
cp config.production.env .env

# Editar valores
nano .env

# Executar aplicação
python backend/main.py
```

## 📊 Verificação da Configuração

### 1. Health Check
```bash
curl https://redacao.admin.recifemais.com.br/health
```

### 2. Verificar Auth
```bash
curl https://redacao.admin.recifemais.com.br/admin/setup/initial-admin \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"123456"}'
```

### 3. Logs do Sistema
```bash
# Verificar logs para erros de configuração
tail -f logs/app.log
```

## 🆘 Troubleshooting

### Erro: "SECRET_KEY not configured"
```env
# Adicionar chave secura
SECRET_KEY=sua_chave_secreta_256_bits
```

### Erro: "Gmail OAuth failed"
```env
# Verificar credenciais Gmail
GMAIL_CLIENT_ID=correto_client_id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=correto_client_secret
```

### Erro: "CORS blocked"
```env
# Adicionar domínio permitido
CORS_ORIGINS=https://seu_dominio.com,https://outro_dominio.com
```

### Erro: "Database connection failed"
```env
# Verificar credenciais Supabase
SUPABASE_URL=https://projeto.supabase.co
SUPABASE_SERVICE_KEY=sua_service_key_correta
```

## 📚 Referências

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Google Cloud Console](https://console.cloud.google.com)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Railway Environment Variables](https://docs.railway.app/develop/variables)

---

**✅ Configuração Completa**: Use `config_updated.env` como referência  
**🚀 Configuração Rápida**: Use `config.production.env` para deploy imediato  
**📖 Documentação**: Consulte `docs/AUTHENTICATION_GUIDE.md` para detalhes 