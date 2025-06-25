#!/bin/bash

# 🔄 Script de Deploy Forçado - RecifeMais Conteúdo
# Este script força a atualização completa do código em produção

echo "🚀 Iniciando deploy forçado..."

# 1. Parar containers atuais
echo "🛑 Parando containers..."
docker-compose -f docker-compose.prod.yml down

# 2. Remover imagens antigas (força rebuild)
echo "🗑️ Removendo imagens antigas..."
docker rmi app-conteudo-recifemais-app 2>/dev/null || true
docker system prune -f

# 3. Pull do código mais recente
echo "📥 Atualizando código..."
git fetch origin
git reset --hard origin/main
git pull origin main

# 3.1. Atualizar variáveis de ambiente se necessário
echo "🔧 Verificando variáveis de ambiente..."
if [ -f "config.prod.env" ]; then
    echo "✅ Usando config.prod.env atualizado"
    cp config.prod.env .env
else
    echo "⚠️ config.prod.env não encontrado, mantendo .env atual"
fi

# 4. Rebuild completo sem cache
echo "🔨 Fazendo rebuild completo..."
docker-compose -f docker-compose.prod.yml build --no-cache

# 5. Iniciar containers
echo "▶️ Iniciando containers..."
docker-compose -f docker-compose.prod.yml up -d

# 6. Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 10

# 7. Verificar status
echo "🔍 Verificando status..."
docker-compose -f docker-compose.prod.yml ps

# 8. Testar health check
echo "🏥 Testando health check..."
sleep 5
curl -s http://localhost:8001/health | python3 -m json.tool || echo "❌ Health check falhou"

# 9. Mostrar logs recentes
echo "📋 Logs recentes:"
docker-compose -f docker-compose.prod.yml logs --tail=20 app

echo "✅ Deploy concluído!"
echo "🔗 Acesse: http://localhost:8001/"
echo "📊 Health: http://localhost:8001/health" 