# 🔐 **CREDENCIAIS GOOGLE NECESSÁRIAS**
## **Lista Completa para Configuração da Aplicação RecifeMais**

---

## **📋 RESUMO EXECUTIVO**

Para que a aplicação RecifeMais funcione completamente, precisamos configurar **4 integrações Google** diferentes. Este documento lista exatamente o que é necessário para cada uma.

---

## **🎯 CREDENCIAIS OBRIGATÓRIAS (FUNCIONAMENTO BÁSICO)**

### **1. GOOGLE GEMINI AI** ⭐ **PRIORIDADE MÁXIMA**

#### **O que é necessário:**
- ✅ **API Key do Google AI Studio**
- ✅ **Projeto Google Cloud** (pode ser o mesmo dos outros)

#### **Como obter:**
1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada (formato: `AIzaSy...`)

#### **Onde usar:**
```bash
# No arquivo .env
GOOGLE_AI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### **Função na aplicação:**
- Processamento de emails de assessoria
- Geração de conteúdo otimizado
- Análise de sentimento

---

### **2. GMAIL API** ⭐ **PRIORIDADE MÁXIMA**

#### **O que é necessário:**
- ✅ **Client ID OAuth 2.0**
- ✅ **Client Secret OAuth 2.0**
- ✅ **Conta Gmail** para conectar

#### **Como obter:**
1. Acesse: https://console.cloud.google.com/
2. Crie ou selecione um projeto
3. Vá em "APIs & Services" > "Credentials"
4. Clique "+ CREATE CREDENTIALS" > "OAuth client ID"
5. Escolha "Web application"
6. Configure:
   - **Name:** RecifeMais Gmail Integration
   - **Authorized redirect URIs:** `http://localhost:8001/auth/callback`
7. Copie Client ID e Client Secret

#### **APIs para habilitar:**
- Gmail API
- Google+ API (para profile info)

#### **Onde usar:**
```bash
# No arquivo .env
GMAIL_CLIENT_ID=123456789-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxx
GMAIL_REDIRECT_URI=http://localhost:8001/auth/callback
```

#### **Função na aplicação:**
- Coleta automática de emails de assessorias
- Marcação de emails processados

---

## **🎯 CREDENCIAIS OPCIONAIS (FUNCIONALIDADES AVANÇADAS)**

### **3. GOOGLE SEARCH CONSOLE API** ⚠️ **OPCIONAL MAS RECOMENDADO**

#### **O que é necessário:**
- ✅ **Mesmo Client ID/Secret do Gmail** (pode reutilizar)
- ✅ **Site verificado** no Google Search Console
- ✅ **Permissões de proprietário** no site

#### **Como obter:**
1. **Reutilizar credenciais OAuth do Gmail** (mesmo Client ID/Secret)
2. **Verificar site no GSC:**
   - Acesse: https://search.google.com/search-console
   - Adicione propriedade: `https://recifemais.com.br`
   - Escolha método de verificação (HTML tag recomendado)
   - Confirme verificação

#### **APIs para habilitar:**
- Google Search Console API

#### **Onde usar:**
```bash
# No arquivo .env (mesmo do Gmail)
GSC_SITE_URL=https://recifemais.com.br/
```

#### **Função na aplicação:**
- Análise de performance SEO
- Monitoramento de palavras-chave
- Insights de conteúdo

---

### **4. GOOGLE ANALYTICS 4 API** ⚠️ **OPCIONAL MAS RECOMENDADO**

#### **O que é necessário:**
- ✅ **Mesmo Client ID/Secret do Gmail** (pode reutilizar)
- ✅ **Property ID do GA4**
- ✅ **Permissões de visualização** no GA4

#### **Como obter:**
1. **Reutilizar credenciais OAuth do Gmail** (mesmo Client ID/Secret)
2. **Obter Property ID do GA4:**
   - Acesse: https://analytics.google.com/
   - Selecione a propriedade do RecifeMais
   - Vá em Admin > Property Settings
   - Copie o "Property ID" (formato: `123456789`)

#### **APIs para habilitar:**
- Google Analytics Data API

#### **Onde usar:**
```bash
# No arquivo .env
GA4_PROPERTY_ID=123456789
```

#### **Função na aplicação:**
- Métricas de audiência detalhadas
- Comportamento do usuário
- Análise de conversões

---

## **📋 CHECKLIST DE CONFIGURAÇÃO**

### **Passo 1: Google Cloud Console Setup**
- [ ] Criar/selecionar projeto Google Cloud
- [ ] Habilitar APIs necessárias:
  - [ ] Gmail API
  - [ ] Google Search Console API (opcional)
  - [ ] Google Analytics Data API (opcional)

### **Passo 2: Credenciais OAuth**
- [ ] Criar OAuth 2.0 Client ID
- [ ] Configurar redirect URI: `http://localhost:8001/auth/callback`
- [ ] Copiar Client ID e Client Secret

### **Passo 3: API Keys**
- [ ] Criar API Key no Google AI Studio
- [ ] Copiar chave do Gemini

### **Passo 4: Configurações de Site**
- [ ] Verificar site no Google Search Console (opcional)
- [ ] Obter Property ID do Google Analytics 4 (opcional)

### **Passo 5: Configurar Aplicação**
- [ ] Adicionar credenciais no arquivo `.env`
- [ ] Testar conexões através dos endpoints

---

## **🔧 ARQUIVO .ENV COMPLETO**

```bash
# Configurações básicas
BASE_URL=http://localhost:8001

# Supabase (já configurado)
SUPABASE_URL=https://aoyrpadrrsckxbuadcnf.supabase.co
SUPABASE_ANON_KEY=sua_chave_anon
SUPABASE_SERVICE_ROLE_KEY=sua_chave_service

# Google AI (OBRIGATÓRIO)
GOOGLE_AI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Gmail OAuth (OBRIGATÓRIO)
GMAIL_CLIENT_ID=123456789-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxx
GMAIL_REDIRECT_URI=http://localhost:8001/auth/callback

# Google Search Console (OPCIONAL)
GSC_SITE_URL=https://recifemais.com.br/

# Google Analytics 4 (OPCIONAL)
GA4_PROPERTY_ID=123456789

# WordPress (já configurado?)
WORDPRESS_URL=https://recifemais.com.br
WORDPRESS_USERNAME=seu_usuario
WORDPRESS_APP_PASSWORD=sua_senha_app
```

---

## **🧪 COMO TESTAR AS INTEGRAÇÕES**

### **1. Testar Gemini AI:**
```bash
curl http://localhost:8001/health
# Deve mostrar "google_ai": true
```

### **2. Testar Gmail OAuth:**
```bash
# 1. Iniciar autenticação
curl http://localhost:8001/auth/gmail
# 2. Seguir URL retornada
# 3. Verificar status
curl http://localhost:8001/gmail/status
```

### **3. Testar Google Data (GSC + GA4):**
```bash
# 1. Iniciar autenticação
curl http://localhost:8001/auth/google
# 2. Seguir URL retornada
# 3. Verificar status
curl http://localhost:8001/google-data/status
```

---

## **⚠️ PROBLEMAS COMUNS E SOLUÇÕES**

### **Problema: "OAuth client not found"**
- **Causa:** Client ID incorreto ou projeto errado
- **Solução:** Verificar se copiou Client ID completo

### **Problema: "Redirect URI mismatch"**
- **Causa:** URI de callback não configurada
- **Solução:** Adicionar `http://localhost:8001/auth/callback` nas URIs autorizadas

### **Problema: "API not enabled"**
- **Causa:** API não habilitada no Google Cloud Console
- **Solução:** Habilitar APIs necessárias no console

### **Problema: "Site not verified in Search Console"**
- **Causa:** Site não verificado no GSC
- **Solução:** Verificar site seguindo processo do GSC

---

## **💡 DICAS IMPORTANTES**

### **Segurança:**
- ✅ **Nunca** commitar credenciais no Git
- ✅ Usar arquivo `.env` local
- ✅ Armazenar credenciais sensíveis no Supabase

### **Desenvolvimento:**
- ✅ Testar uma integração por vez
- ✅ Usar endpoints de health check
- ✅ Verificar logs para debug

### **Produção (futuro):**
- ✅ Usar variáveis de ambiente do servidor
- ✅ Configurar domínio real nos redirect URIs
- ✅ Implementar rate limiting

---

## **🎯 PRÓXIMOS PASSOS**

### **Imediato (Esta Semana):**
1. **Obter credenciais** do Gemini AI e Gmail
2. **Configurar arquivo .env** local
3. **Testar integrações básicas**

### **Opcional (Próxima Semana):**
1. **Configurar Google Search Console**
2. **Configurar Google Analytics 4**
3. **Testar funcionalidades avançadas**

---

**Deyvson, com essas credenciais configuradas, teremos uma aplicação 100% funcional! Vamos começar com o essencial (Gemini + Gmail) e depois expandir para as funcionalidades avançadas. 🚀** 