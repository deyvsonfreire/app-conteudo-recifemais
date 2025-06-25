# 🔥 HOTFIX - Erro de Import wordpress_publisher

## 🚨 Problema Identificado

**Erro:** `ImportError: cannot import name 'wordpress_publisher' from 'backend.modules.wordpress_publisher'`

**Status:** ✅ CORRIGIDO no código (commits 79c007d e b8c95e7)

**Problema:** O ambiente de produção ainda tem a versão antiga do código

## 🛠️ Solução Imediata

### **Opção 1: Script Automático (RECOMENDADO)**

```bash
# No servidor de produção
cd /caminho/para/app-conteudo-recifemais
./scripts/force_deploy.sh
```

### **Opção 2: Comandos Manuais**

```bash
# 1. Parar aplicação
docker-compose -f docker-compose.prod.yml down

# 2. Forçar atualização do código
git fetch origin
git reset --hard origin/main
git pull origin main

# 3. Rebuild sem cache
docker-compose -f docker-compose.prod.yml build --no-cache

# 4. Reiniciar aplicação
docker-compose -f docker-compose.prod.yml up -d

# 5. Verificar logs
docker-compose -f docker-compose.prod.yml logs -f app
```

## 🧪 Verificação

```bash
# Testar health check
curl http://localhost:8001/health

# Deve retornar algo como:
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

## 📋 O que foi Corrigido

### **Antes (❌ Incorreto):**
```python
from .modules.wordpress_publisher import wordpress_publisher
```

### **Depois (✅ Correto):**
```python
from .modules.wordpress_publisher import wp_publisher
```

### **Arquivos Alterados:**
- `backend/main.py` - Todas as referências corrigidas
- `backend/config.py` - Versão atualizada para 2.2.1

## 🔍 Commits Relacionados

- **79c007d** - 🔧 Corrigido import wordpress_publisher -> wp_publisher
- **b8c95e7** - 📝 Atualizada versão para 2.2.1

## 📞 Suporte

Se o problema persistir:

1. **Verificar logs detalhados:**
   ```bash
   docker-compose -f docker-compose.prod.yml logs app > debug.log
   ```

2. **Verificar versão do código:**
   ```bash
   git log --oneline -5
   # Deve mostrar os commits b8c95e7 e 79c007d
   ```

3. **Verificar se o arquivo foi atualizado:**
   ```bash
   grep "wp_publisher" backend/main.py
   # Deve encontrar a linha correta
   ```

---

**Status:** �� PRONTO PARA DEPLOY 