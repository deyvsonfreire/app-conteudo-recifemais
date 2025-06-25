# 🚀 INSTRUÇÕES DE DEPLOY - RecifeMais Conteúdo v2.4.0

## 📋 PRÉ-REQUISITOS

### Servidor (EasyPanel)
- ✅ Docker e Docker Compose instalados
- ✅ Portas 8001 e 6379 disponíveis
- ✅ Acesso SSH ao servidor
- ✅ Git instalado

### Credenciais Necessárias
- ✅ Supabase: URLs e chaves já configuradas
- ✅ Gmail API: Client ID e Secret já configurados
- ✅ WordPress: Username e Password já configurados
- ✅ Google AI: API Key já configurada

## 🎯 PROCESSO DE DEPLOY

### 1. Preparação do Servidor

```bash
# Conectar ao servidor via SSH
ssh user@seu-servidor.com

# Criar diretório do projeto
mkdir -p /var/www/recifemais-conteudo
cd /var/www/recifemais-conteudo

# Clonar repositório
git clone https://github.com/deyvsonfreire/app-conteudo-recifemais.git .

# Verificar se todos os arquivos estão presentes
ls -la
```

### 2. Configuração de Ambiente

```bash
# Criar arquivo .env.production
cp config.prod.env .env.production

# Editar configurações específicas do servidor (se necessário)
nano .env.production

# Verificar configurações
cat .env.production
```

### 3. Deploy Automatizado

```bash
# Executar script de deploy
./deploy.sh
```

### 4. Deploy Manual (Alternativo)

```bash
# Parar containers existentes
docker-compose -f docker-compose.prod.yml down

# Construir imagem
docker-compose -f docker-compose.prod.yml build --no-cache

# Iniciar serviços
docker-compose -f docker-compose.prod.yml up -d

# Verificar status
docker-compose -f docker-compose.prod.yml ps
```

## 🧪 TESTES DE PRODUÇÃO

### 1. Health Check
```bash
curl http://localhost:8001/health
```
**Resposta esperada:**
```json
{
  "status": "healthy",
  "checks": {
    "database": true,
    "wordpress": true,
    "gemini": true,
    "gmail": true,
    "google_data": true,
    "auth": true
  }
}
```

### 2. API Info
```bash
curl http://localhost:8001/api
```

### 3. Gmail Status
```bash
curl http://localhost:8001/gmail/status
```

### 4. WordPress Connection
```bash
curl http://localhost:8001/wordpress/posts
```

### 5. Interface Web
Acessar: `http://localhost:8001/`

## 📊 MONITORAMENTO

### Logs da Aplicação
```bash
# Ver logs em tempo real
docker logs recifemais-backend -f

# Ver últimas 100 linhas
docker logs recifemais-backend --tail 100
```

### Status dos Containers
```bash
# Ver status
docker-compose -f docker-compose.prod.yml ps

# Ver uso de recursos
docker stats
```

### Health Check Contínuo
```bash
# Criar script de monitoramento
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        echo "$(date): ✅ Sistema OK"
    else
        echo "$(date): ❌ Sistema com problemas"
    fi
    sleep 60
done
EOF

chmod +x monitor.sh
./monitor.sh
```

## 🔧 COMANDOS ÚTEIS

### Gerenciamento de Containers
```bash
# Reiniciar aplicação
docker-compose -f docker-compose.prod.yml restart app

# Reiniciar Redis
docker-compose -f docker-compose.prod.yml restart redis

# Ver logs específicos
docker logs recifemais-backend
docker logs recifemais-redis

# Entrar no container
docker exec -it recifemais-backend bash
```

### Backup e Manutenção
```bash
# Backup do Redis
docker exec recifemais-redis redis-cli BGSAVE

# Limpar logs antigos
docker system prune -f

# Atualizar código
git pull origin main
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

## 🌐 CONFIGURAÇÃO NGINX (Opcional)

Se usar Nginx como proxy reverso:

```bash
# Iniciar com Nginx
docker-compose -f docker-compose.prod.yml --profile nginx up -d

# Configurar SSL (Let's Encrypt)
# [Instruções específicas do seu servidor]
```

## 🚨 SOLUÇÃO DE PROBLEMAS

### Aplicação não inicia
```bash
# Verificar logs
docker logs recifemais-backend

# Verificar variáveis de ambiente
docker exec recifemais-backend env | grep -E "(SUPABASE|GMAIL|WORDPRESS)"

# Testar conexões
docker exec recifemais-backend curl -f http://localhost:8001/health
```

### Redis não conecta
```bash
# Verificar status do Redis
docker exec recifemais-redis redis-cli ping

# Reiniciar Redis
docker-compose -f docker-compose.prod.yml restart redis
```

### Problemas de permissão
```bash
# Ajustar permissões
sudo chown -R 1000:1000 ./logs
```

## 📞 SUPORTE

Em caso de problemas:
1. Verificar logs da aplicação
2. Testar health check
3. Verificar conectividade com Supabase
4. Verificar credenciais no banco de dados

## ✅ CHECKLIST DE DEPLOY

- [ ] Servidor preparado com Docker
- [ ] Repositório clonado
- [ ] Arquivo .env.production configurado
- [ ] Script de deploy executado
- [ ] Health check respondendo
- [ ] Gmail autenticado
- [ ] WordPress conectado
- [ ] Interface web acessível
- [ ] Logs sendo gerados corretamente
- [ ] Monitoramento configurado

---

**🎉 Deploy concluído com sucesso!**

O sistema RecifeMais Conteúdo v2.4.0 está pronto para uso em produção. 