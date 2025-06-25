# 🚀 Deploy no EasyPanel - RecifeMais Conteúdo

## 📋 Pré-requisitos

- ✅ Servidor com EasyPanel instalado
- ✅ Docker e Docker Compose funcionando
- ✅ Acesso SSH ao servidor
- ✅ Domínio configurado (opcional)

## 🔧 Processo de Deploy

### **1. Clonar o Repositório**

```bash
# No servidor via SSH
git clone https://github.com/deyvsonfreire/app-conteudo-recifemais.git
cd app-conteudo-recifemais
```

### **2. Configurar Variáveis de Ambiente**

```bash
# Copiar e editar configurações
cp config.prod.env .env
nano .env

# Adicionar suas credenciais reais:
# - Supabase keys
# - Google AI key
# - Gmail credentials
# - WordPress credentials
```

### **3. Deploy via EasyPanel**

#### **Opção A: Via Interface EasyPanel**
1. Acesse o painel do EasyPanel
2. Crie novo projeto "RecifeMais Conteúdo"
3. Configure Git repository: `https://github.com/deyvsonfreire/app-conteudo-recifemais.git`
4. Use o `docker-compose.prod.yml`
5. Configure variáveis de ambiente
6. Deploy!

#### **Opção B: Via Docker Compose Manual**

```bash
# Build e start dos containers
docker-compose -f docker-compose.prod.yml up -d

# Verificar logs
docker-compose -f docker-compose.prod.yml logs -f app

# Verificar status
docker-compose -f docker-compose.prod.yml ps
```

### **4. Configurar Nginx (se necessário)**

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **5. Configurar SSL (Opcional)**

```bash
# Usando Certbot
sudo certbot --nginx -d seu-dominio.com
```

## 🧪 Testes Pós-Deploy

### **Verificar Health Check**
```bash
curl http://seu-servidor:8001/health
```

### **Testar Endpoints Principais**
```bash
# Status geral
curl http://seu-servidor:8001/

# Listar emails
curl http://seu-servidor:8001/emails

# Status Gmail
curl http://seu-servidor:8001/gmail/status
```

## 📊 Monitoramento

### **Logs em Tempo Real**
```bash
# Logs da aplicação
docker logs -f recifemais-backend

# Logs do Redis
docker logs -f recifemais-redis

# Logs do PostgreSQL (se usar local)
docker logs -f recifemais-db
```

### **Métricas de Sistema**
```bash
# Uso de recursos
docker stats

# Status dos containers
docker ps

# Espaço em disco
df -h
```

## 🔄 Atualizações

### **Deploy de Nova Versão**
```bash
# Pull do código atualizado
git pull origin main

# Rebuild e restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

## 🚨 Troubleshooting

### **Problemas Comuns**

1. **Container não inicia**
   ```bash
   docker-compose -f docker-compose.prod.yml logs app
   ```

2. **Erro de conexão com banco**
   - Verificar credenciais no `.env`
   - Testar conectividade: `docker exec -it recifemais-backend ping postgres`

3. **Erro de DNS/IA**
   - Verificar conectividade externa: `docker exec -it recifemais-backend ping google.com`
   - Verificar API key do Google AI

4. **Erro do Gmail**
   - Verificar OAuth credentials
   - Reautenticar se necessário

## 📞 Suporte

- **Logs completos**: `docker-compose -f docker-compose.prod.yml logs > debug.log`
- **Status detalhado**: `curl http://localhost:8001/health | jq`
- **Métricas**: Acessar EasyPanel dashboard

---

**🎯 Com EasyPanel teremos controle total e logs completos para debugging!** 