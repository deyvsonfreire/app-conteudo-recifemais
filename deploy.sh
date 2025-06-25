#!/bin/bash

# ===========================================
# RECIFEMAIS CONTEÚDO - DEPLOY SCRIPT v2.5.0
# ===========================================
# 🚀 Deploy otimizado para EasyPanel
# ===========================================

set -e  # Exit on any error

echo "🚀 Iniciando deploy do RecifeMais Conteúdo v2.5.0..."

# Verificar se estamos no diretório correto
if [ ! -f "backend/main.py" ]; then
    echo "❌ Erro: Execute este script na raiz do projeto"
    exit 1
fi

# Copiar configuração de produção
echo "📋 Configurando ambiente de produção..."
cp config.prod.env .env

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Erro: Docker não está rodando"
    exit 1
fi

# Build da imagem
echo "🔨 Construindo imagem Docker..."
docker build -t recifemais-conteudo:latest .

# Verificar se a build foi bem-sucedida
if [ $? -ne 0 ]; then
    echo "❌ Erro na build da imagem Docker"
    exit 1
fi

echo "✅ Build concluída com sucesso!"

# Testar a imagem localmente (opcional)
echo "🧪 Testando imagem..."
docker run --rm -d --name recifemais-test -p 8001:8001 \
    -e SUPABASE_URL="https://aoyrpadrrsckxbuadcnf.supabase.co" \
    -e SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MDY5MTksImV4cCI6MjA2NjM4MjkxOX0.BAkMkcWzUeLL9_G-qAEdOX-Nhjmr5WLSv_AOqvdxA74" \
    recifemais-conteudo:latest

# Aguardar container inicializar
sleep 10

# Testar health check
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Teste de saúde passou!"
    docker stop recifemais-test
else
    echo "⚠️ Teste de saúde falhou, mas continuando deploy..."
    docker stop recifemais-test || true
fi

echo ""
echo "🎉 Deploy preparado com sucesso!"
echo ""
echo "📋 PRÓXIMOS PASSOS NO EASYPANEL:"
echo ""
echo "1. 📁 UPLOAD:"
echo "   - Faça upload de todo o projeto para o EasyPanel"
echo "   - Ou use Git deploy se conectado ao repositório"
echo ""
echo "2. ⚙️ CONFIGURAÇÃO:"
echo "   - Porta: 8001"
echo "   - Comando: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001"
echo "   - Dockerfile: Usar o Dockerfile existente"
echo ""
echo "3. 🌐 VARIÁVEIS DE AMBIENTE:"
echo "   - Copie o conteúdo de config.prod.env"
echo "   - Ou configure as variáveis principais:"
echo "     * SUPABASE_URL=https://aoyrpadrrsckxbuadcnf.supabase.co"
echo "     * SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
echo "     * ENVIRONMENT=production"
echo ""
echo "4. 🚀 APÓS DEPLOY:"
echo "   - Acesse: https://seu-dominio.easypanel.host/health/dashboard"
echo "   - Execute migração: https://seu-dominio.easypanel.host/admin/migrate-credentials"
echo "   - Configure OAuth: https://seu-dominio.easypanel.host/auth/gmail"
echo ""
echo "📞 SUPORTE:"
echo "   - Health Check: /health"
echo "   - Dashboard: /health/dashboard"
echo "   - Logs: /admin/stats/realtime"
echo ""
echo "🔗 ENDPOINTS PRINCIPAIS:"
echo "   - Interface: /"
echo "   - API Docs: /docs"
echo "   - Admin: /admin/secure-config"
echo "   - Gmail Auth: /auth/gmail"
echo "" 