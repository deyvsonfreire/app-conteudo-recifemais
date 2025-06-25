#!/bin/bash

# ===========================================
# SCRIPT DE DEPLOY - RecifeMais Conteúdo v2.4.0
# ===========================================

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do RecifeMais Conteúdo v2.4.0..."

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Erro: Execute este script do diretório raiz do projeto"
    exit 1
fi

# Verificar se o arquivo .env.production existe
if [ ! -f ".env.production" ]; then
    echo "❌ Erro: Arquivo .env.production não encontrado"
    echo "📝 Criando arquivo .env.production..."
    cp config.prod.env .env.production
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose -f docker-compose.prod.yml down --remove-orphans

# Limpar imagens antigas (opcional)
echo "🧹 Limpando imagens antigas..."
docker system prune -f

# Construir nova imagem
echo "🔨 Construindo nova imagem..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Iniciar serviços
echo "▶️ Iniciando serviços..."
docker-compose -f docker-compose.prod.yml up -d

# Aguardar inicialização
echo "⏳ Aguardando inicialização dos serviços..."
sleep 30

# Verificar saúde dos serviços
echo "🏥 Verificando saúde dos serviços..."

# Testar Redis
if docker exec recifemais-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis: OK"
else
    echo "❌ Redis: FALHOU"
fi

# Testar aplicação
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Aplicação: OK"
    
    # Mostrar status detalhado
    echo "📊 Status detalhado:"
    curl -s http://localhost:8001/health | jq . 2>/dev/null || curl -s http://localhost:8001/health
else
    echo "❌ Aplicação: FALHOU"
    echo "📋 Logs da aplicação:"
    docker logs recifemais-backend --tail 20
fi

# Mostrar informações finais
echo ""
echo "🎉 Deploy concluído!"
echo "📍 URLs disponíveis:"
echo "   - Health Check: http://localhost:8001/health"
echo "   - API Info: http://localhost:8001/api"
echo "   - Documentação: http://localhost:8001/docs"
echo "   - Interface: http://localhost:8001/"
echo ""
echo "📋 Comandos úteis:"
echo "   - Ver logs: docker logs recifemais-backend -f"
echo "   - Parar: docker-compose -f docker-compose.prod.yml down"
echo "   - Reiniciar: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "✨ Sistema pronto para uso!" 