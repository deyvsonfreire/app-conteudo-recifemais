# **Documentação da Aplicação: Automação Inteligente de Conteúdo - V2 OTIMIZADA**

## **O Cofundador de Conteúdo Estratégico para Recifemais.com.br**

## **1. Visão Geral e Propósito (V2 Otimizada)**

Esta V2 da aplicação é um sistema de inteligência editorial abrangente, desenhado para empoderar o Recifemais.com.br a ser a **principal referência digital** sobre a cidade de Recife. Indo além da automação de rascunhos, ela atua como um **"Cofundador de Conteúdo Estratégico"**, gerando, otimizando e sugerindo pautas que ressoam profundamente com o "Conectado Recifense" e se alinham perfeitamente com a proposta de valor "Alma e Pulso" do portal.

### **Filosofia de Desenvolvimento: MVP First + Iteração Inteligente**

Adotamos uma abordagem de desenvolvimento em **fases incrementais**, priorizando:
- **ROI imediato** com funcionalidades core
- **Validação rápida** através de protótipos
- **Otimização de custos** de IA desde o início
- **Escalabilidade** planejada para SaaS futuro

## **2. Cronograma de Desenvolvimento Estruturado**

### **FASE 1: MVP Core (4-6 semanas) 🚀**
**Objetivo:** Sistema funcional básico com ROI imediato

**Semana 1-2: Fundação Técnica**
- [ ] Setup do ambiente de desenvolvimento
- [ ] Configuração do Supabase (DB + Auth)
- [ ] Estrutura básica do backend FastAPI
- [ ] Configuração de credenciais e variáveis de ambiente
- [ ] Sistema de logging estruturado

**Semana 3-4: Core Funcional**
- [ ] `email_collector.py` - Integração Gmail funcional
- [ ] `ai_processor.py` - Processamento básico com Gemini
- [ ] `wordpress_publisher.py` - Publicação de rascunhos
- [ ] Tabelas essenciais no Supabase
- [ ] Cache básico com Redis

**Semana 5-6: Interface e Integração**
- [ ] Dashboard React mínimo mas funcional
- [ ] Sistema de aprovação de rascunhos
- [ ] Testes automatizados básicos
- [ ] Deploy em ambiente de produção
- [ ] Monitoramento básico com Sentry

**Entregáveis Fase 1:**
- ✅ Sistema processando emails reais
- ✅ Geração de rascunhos com Gemini
- ✅ Publicação no WordPress
- ✅ Dashboard para aprovação
- ✅ Métricas básicas de uso

### **FASE 2: Inteligência Estratégica (6-8 semanas) 🧠**
**Objetivo:** Implementar IA avançada e integração Google

**Semana 7-10: APIs Google e RAG**
- [ ] `google_data_connector.py` - GSC, GA4, Trends
- [ ] Sistema RAG com embeddings (pgvector)
- [ ] `knowledge_base` - Indexação de conteúdo
- [ ] Cache multinível otimizado
- [ ] Sistema de priorização de pautas

**Semana 11-14: Feedback Loop e Otimização**
- [ ] `feedback_loop_monitor.py` - Análise de performance
- [ ] Sugestões proativas de pautas
- [ ] Otimização automática de prompts
- [ ] Sistema de custos e rate limiting
- [ ] Dashboard de analytics avançado

**Entregáveis Fase 2:**
- ✅ Sugestões proativas baseadas em dados
- ✅ Análise de lacunas SEO
- ✅ Sistema RAG funcional
- ✅ Feedback loop automatizado
- ✅ Otimização de custos de IA

### **FASE 3: Experiência Avançada (8-10 semanas) 🎨**
**Objetivo:** Dashboard completo e recursos colaborativos

**Semana 15-20: Dashboard Premium**
- [ ] Interface colaborativa avançada
- [ ] Sistema de versionamento de conteúdo
- [ ] Aprovação com workflow
- [ ] Métricas visuais interativas
- [ ] Gestão de equipe e permissões

**Semana 21-24: Recursos Avançados**
- [ ] Análise de sentimento
- [ ] Integração redes sociais
- [ ] Sistema de templates
- [ ] API pública para integrações
- [ ] Documentação completa

**Entregáveis Fase 3:**
- ✅ Plataforma SaaS-ready
- ✅ Colaboração multi-usuário
- ✅ Analytics avançados
- ✅ Integrações externas
- ✅ Sistema de templates

## **3. Estrutura de Arquivos Completa**

```
app-conteudo-recifemais/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
│
├── backend/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app principal
│   ├── config.py                        # Configurações e env vars
│   ├── database.py                      # Conexão Supabase
│   ├── dependencies.py                  # Dependências FastAPI
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py                  # Autenticação e segurança
│   │   ├── cache.py                     # Sistema de cache Redis
│   │   ├── logging.py                   # Logging estruturado
│   │   └── exceptions.py                # Exceções customizadas
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── email_collector.py           # Coleta de emails Gmail
│   │   ├── preprocessor_cache.py        # Pré-processamento inteligente
│   │   ├── ai_processor.py              # Processamento IA (Gemini)
│   │   ├── wordpress_publisher.py       # Publicação WordPress
│   │   ├── google_data_connector.py     # APIs Google (GSC, GA, Trends)
│   │   ├── feedback_loop_monitor.py     # Monitoramento performance
│   │   └── knowledge_manager.py         # Gestão RAG e embeddings
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── email.py                     # Modelos de email
│   │   ├── content.py                   # Modelos de conteúdo
│   │   ├── analytics.py                 # Modelos de métricas
│   │   └── user.py                      # Modelos de usuário
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── emails.py                # Endpoints de email
│   │   │   ├── content.py               # Endpoints de conteúdo
│   │   │   ├── analytics.py             # Endpoints de analytics
│   │   │   ├── pautas.py                # Endpoints de pautas
│   │   │   └── admin.py                 # Endpoints administrativos
│   │   └── middleware.py                # Middlewares personalizados
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── email_service.py             # Lógica de negócio emails
│   │   ├── ai_service.py                # Lógica de negócio IA
│   │   ├── seo_service.py               # Lógica de negócio SEO
│   │   └── analytics_service.py         # Lógica de negócio analytics
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── text_processing.py           # Processamento de texto
│   │   ├── embeddings.py                # Utilitários embeddings
│   │   ├── prompt_templates.py          # Templates de prompts
│   │   └── validators.py                # Validadores customizados
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── email.py                     # Schemas Pydantic email
│   │   ├── content.py                   # Schemas Pydantic conteúdo
│   │   └── analytics.py                 # Schemas Pydantic analytics
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py               # Configuração Celery
│   │   ├── email_tasks.py              # Tasks assíncronas email
│   │   ├── ai_tasks.py                 # Tasks assíncronas IA
│   │   └── monitoring_tasks.py         # Tasks de monitoramento
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py                 # Configuração pytest
│       ├── test_email_collector.py
│       ├── test_ai_processor.py
│       ├── test_api/
│       └── test_services/
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   │
│   ├── src/
│   │   ├── app/                        # Next.js 14 App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── emails/
│   │   │   │   ├── pautas/
│   │   │   │   ├── analytics/
│   │   │   │   └── settings/
│   │   │   └── api/                    # API routes Next.js
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                     # shadcn/ui components
│   │   │   ├── dashboard/
│   │   │   │   ├── EmailList.tsx
│   │   │   │   ├── ContentEditor.tsx
│   │   │   │   ├── AnalyticsDashboard.tsx
│   │   │   │   └── PautaSuggestions.tsx
│   │   │   ├── forms/
│   │   │   └── common/
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts                  # Cliente API
│   │   │   ├── auth.ts                 # Autenticação
│   │   │   ├── utils.ts                # Utilitários
│   │   │   └── stores/                 # Zustand stores
│   │   │
│   │   ├── hooks/
│   │   │   ├── useEmails.ts
│   │   │   ├── useAnalytics.ts
│   │   │   └── useAuth.ts
│   │   │
│   │   └── types/
│   │       ├── api.ts
│   │       ├── content.ts
│   │       └── analytics.ts
│   │
│   └── public/
│       ├── icons/
│       └── images/
│
├── database/
│   ├── migrations/                     # Migrations Supabase
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_add_knowledge_base.sql
│   │   └── 003_add_analytics.sql
│   ├── seeds/                          # Dados iniciais
│   └── schemas/                        # Esquemas SQL
│
├── docs/
│   ├── API.md                          # Documentação API
│   ├── DEPLOYMENT.md                   # Guia de deploy
│   ├── DEVELOPMENT.md                  # Guia de desenvolvimento
│   └── ARCHITECTURE.md                 # Documentação arquitetura
│
├── scripts/
│   ├── setup.sh                       # Setup inicial
│   ├── deploy.sh                       # Script de deploy
│   ├── backup.sh                       # Backup banco de dados
│   └── migrate.py                      # Migrações manuais
│
└── monitoring/
    ├── docker-compose.monitoring.yml   # Stack monitoramento
    ├── prometheus.yml                  # Configuração Prometheus
    └── grafana/                        # Dashboards Grafana
```

## **4. Stack Tecnológico Otimizado**

### **Backend Core**
```python
# requirements.txt principais
fastapi[all]==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.7
redis==5.0.1
celery==5.3.4
sentry-sdk[fastapi]==1.38.0

# AI/ML
google-generativeai==0.3.1
langchain==0.1.0
tiktoken==0.5.1
instructor==0.4.5
numpy==1.24.3
scipy==1.11.4

# Google APIs
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-api-python-client==2.108.0
pytrends==4.9.2

# Utilitários
httpx==0.25.2
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

### **Frontend Moderno**
```json
// package.json principais
{
  "dependencies": {
    "next": "14.0.3",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "@tanstack/react-query": "5.8.4",
    "zustand": "4.4.7",
    "tailwindcss": "3.3.6",
    "@radix-ui/react-*": "latest",
    "recharts": "2.8.0",
    "framer-motion": "10.16.5",
    "lucide-react": "0.294.0"
  }
}
```

## **5. Modelagem de Dados Otimizada (Supabase)**

### **Tabelas Core (Fase 1)**
```sql
-- Email Cache Otimizada
CREATE TABLE email_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_hash VARCHAR(64) UNIQUE NOT NULL,
    sender VARCHAR(255) NOT NULL,
    subject TEXT NOT NULL,
    content_text TEXT,
    received_at TIMESTAMP WITH TIME ZONE NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending',
    
    -- Processamento IA
    gemini_prompt TEXT,
    gemini_response JSONB,
    tokens_used_input INTEGER DEFAULT 0,
    tokens_used_output INTEGER DEFAULT 0,
    processing_cost_usd DECIMAL(10,4) DEFAULT 0,
    
    -- WordPress Integration
    wordpress_post_id INTEGER,
    wordpress_status VARCHAR(20),
    
    -- Categorização
    detected_category VARCHAR(50),
    priority_score INTEGER DEFAULT 5,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Knowledge Base para RAG
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_text TEXT NOT NULL,
    embedding VECTOR(1536), -- text-embedding-3-small
    
    source_url TEXT,
    source_type VARCHAR(50), -- 'post', 'guideline', 'assessoria_info'
    topic VARCHAR(100),
    category_recifemais VARCHAR(50),
    
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_indexed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Suggested Topics (Pautas Proativas)
CREATE TABLE suggested_topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title_suggestion TEXT NOT NULL,
    summary_suggestion TEXT,
    
    -- SEO Data
    seo_keywords TEXT[],
    search_volume INTEGER,
    competition_score DECIMAL(3,2),
    trend_data JSONB,
    
    -- Targeting
    target_audience_segment VARCHAR(100),
    relevance_score DECIMAL(3,2),
    
    -- Content Suggestions
    suggested_format VARCHAR(50), -- 'article', 'list', 'guide', 'news'
    suggested_multimedia JSONB, -- tipos de mídia sugeridos
    suggested_ugc_cta TEXT,
    
    -- Workflow
    status VARCHAR(20) DEFAULT 'suggested',
    wordpress_post_id INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### **Tabelas Avançadas (Fase 2)**
```sql
-- Performance Monitoring
CREATE TABLE post_performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wordpress_post_id INTEGER NOT NULL,
    post_title TEXT,
    publish_date DATE,
    
    -- Google Search Console Data
    gsc_impressions INTEGER DEFAULT 0,
    gsc_clicks INTEGER DEFAULT 0,
    gsc_ctr DECIMAL(5,4) DEFAULT 0,
    gsc_position DECIMAL(5,2) DEFAULT 0,
    gsc_queries JSONB DEFAULT '[]',
    
    -- Google Analytics Data
    ga_pageviews INTEGER DEFAULT 0,
    ga_unique_pageviews INTEGER DEFAULT 0,
    ga_avg_time_on_page INTEGER DEFAULT 0,
    ga_bounce_rate DECIMAL(5,4) DEFAULT 0,
    ga_demographics JSONB DEFAULT '{}',
    
    -- AI Insights
    ai_insights TEXT,
    performance_score DECIMAL(3,2),
    
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System Configuration
CREATE TABLE system_config (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## **6. APIs Necessárias - SOLICITAÇÃO DE CREDENCIAIS**

Para iniciarmos o desenvolvimento e testes, preciso das seguintes credenciais:

### **🔑 APIs Obrigatórias (Fase 1)**

#### **Google AI Studio (Gemini)**
- [ ] **API Key do Google AI Studio**
- Acesse: https://makersuite.google.com/app/apikey
- Necessário para: Geração de conteúdo e embeddings

#### **Gmail API**
- [ ] **Client ID e Client Secret** (OAuth 2.0)
- [ ] **Refresh Token** ou credenciais de conta de serviço
- Acesse: https://console.cloud.google.com/apis/credentials
- Habilite: Gmail API
- Necessário para: Coleta de emails de assessoria

#### **WordPress API**
- [ ] **URL do site WordPress**
- [ ] **Username/Application Password** ou **JWT Token**
- No WordPress: Usuários → Perfil → Senhas de aplicativo
- Necessário para: Publicação de rascunhos

#### **Supabase**
- [ ] **Project URL**
- [ ] **Anon/Public Key**
- [ ] **Service Role Key** (para operações admin)
- Acesse: https://supabase.com/dashboard/project/[seu-projeto]/settings/api
- Necessário para: Banco de dados e autenticação

### **📊 APIs Opcionais (Fase 2)**

#### **Google Search Console API**
- [ ] **Client ID/Secret** (mesmo do Gmail)
- [ ] **Site URL** verificado no GSC
- Necessário para: Análise de performance SEO

#### **Google Analytics 4 API**
- [ ] **Property ID** do GA4
- [ ] **Credenciais** (mesmo OAuth do Gmail)
- Necessário para: Métricas de audiência

### **⚙️ Configurações Adicionais**

#### **Redis (para cache)**
- [ ] **URL de conexão Redis** (ou usaremos local para desenvolvimento)
- Recomendo: Upstash Redis (plano gratuito)

#### **Monitoramento**
- [ ] **DSN do Sentry** (para error tracking)
- Acesse: https://sentry.io
- Plano gratuito disponível

## **7. Próximos Passos Imediatos**

### **Esta Semana (Protótipo Validação)**
1. **Você fornece as credenciais** das APIs obrigatórias
2. **Eu crio um protótipo** Gmail → Gemini → WordPress
3. **Testamos** com 1-2 emails reais
4. **Validamos** a viabilidade técnica

### **Próxima Semana (Setup Completo)**
1. **Configuração** do ambiente completo
2. **Implementação** do MVP básico
3. **Testes** com volume real de emails
4. **Ajustes** baseados nos resultados

## **8. Estimativa de Custos Operacionais**

### **Mensais Estimados:**
- **Gemini API**: $50-150 (dependendo do volume)
- **Supabase**: $25-50 (Pro plan)
- **Redis**: $0-20 (Upstash)
- **Hosting**: $20-50 (Vercel + Railway)
- **Monitoramento**: $0 (planos gratuitos)

**Total Estimado**: $95-270/mês

### **ROI Esperado:**
- **Tempo economizado**: 15-25h/semana
- **Valor do tempo**: R$ 50-100/hora
- **ROI mensal**: R$ 3.000-10.000
- **Payback**: < 1 mês

---

**Deyvson, estou pronto para começar! Por favor, me envie as credenciais das APIs obrigatórias e vamos colocar este projeto revolucionário no ar! 🚀**

Qual parte você gostaria de iniciar primeiro? Sugiro começarmos com o protótipo Gmail + Gemini para validarmos a integração básica.