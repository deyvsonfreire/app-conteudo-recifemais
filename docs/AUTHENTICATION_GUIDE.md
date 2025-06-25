# 🔐 Guia do Sistema de Autenticação - RecifeMais v2.4.0

## Visão Geral

O sistema de autenticação foi implementado usando **Supabase Auth** com controle de acesso baseado em roles. Oferece segurança robusta, gestão de usuários e interface web moderna.

## 🎯 Funcionalidades

### Backend (API)
- ✅ Autenticação JWT com Supabase Auth
- ✅ Role-based access control (admin, editor, viewer)
- ✅ User management completo (CRUD)
- ✅ Auto-refresh de tokens
- ✅ Session management
- ✅ Middleware de proteção de rotas
- ✅ Health check integrado

### Frontend (Web UI)
- ✅ Tela de login responsiva
- ✅ Dashboard com navegação
- ✅ Gerenciamento de usuários (admin)
- ✅ Setup de admin inicial
- ✅ Monitoramento de sistema
- ✅ Error handling e loading states

## 🚀 Primeiros Passos

### 1. Configuração Inicial

O sistema já está configurado para usar as credenciais do Supabase existentes. Não são necessárias configurações adicionais.

### 2. Criar Admin Inicial

**Primeira vez usando o sistema:**

1. Acesse: https://redacao.admin.recifemais.com.br
2. Clique em "Configurar Admin Inicial"
3. Preencha email e senha
4. Faça login com as credenciais criadas

**Via API (alternativo):**
```bash
curl -X POST https://redacao.admin.recifemais.com.br/admin/setup/initial-admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@recifemais.com.br",
    "password": "senha_segura",
    "role": "admin"
  }'
```

### 3. Acessar o Sistema

1. Acesse: https://redacao.admin.recifemais.com.br
2. Digite email e senha
3. Explore o dashboard

## 👥 Roles e Permissões

### Admin
- **Permissões**: Acesso total (`*`)
- **Pode fazer**:
  - Gerenciar usuários (criar, editar, remover)
  - Acessar todas as seções
  - Configurar sistema
  - Ver estatísticas de auth

### Editor
- **Permissões**: `content`, `analytics`, `wordpress`
- **Pode fazer**:
  - Gerenciar conteúdo
  - Acessar analytics
  - Publicar no WordPress
  - Ver dados do Google

### Viewer
- **Permissões**: `analytics`, `reports`
- **Pode fazer**:
  - Ver analytics
  - Acessar relatórios
  - Visualizar dashboard

## 🔧 Endpoints da API

### Autenticação
```
POST /auth/login          # Login
POST /auth/refresh        # Renovar token
POST /auth/logout         # Logout
GET  /auth/me            # Info do usuário atual
```

### Gerenciamento de Usuários (Admin apenas)
```
GET    /admin/users              # Listar usuários
POST   /admin/users              # Criar usuário
PUT    /admin/users/role         # Atualizar role
DELETE /admin/users/{user_id}    # Remover usuário
GET    /admin/auth/stats         # Estatísticas
```

### Setup Inicial
```
POST /admin/setup/initial-admin  # Criar admin inicial
```

## 💻 Uso da Interface Web

### Dashboard Principal
- **Visão Geral**: Estatísticas do sistema
- **Analytics**: Dados Google Analytics/Search Console
- **Conteúdo**: Gestão de posts e emails
- **Usuários**: Gerenciamento de usuários (admin only)

### Gerenciamento de Usuários
1. Acesse seção "Usuários" (admin only)
2. Clique em "Adicionar Usuário"
3. Preencha email, senha e role
4. Gerencie roles e remova usuários conforme necessário

## 🔒 Segurança

### Tokens JWT
- **Duração**: Configurada no Supabase
- **Auto-refresh**: 5 minutos antes da expiração
- **Armazenamento**: localStorage (frontend)

### Proteção de Rotas
```python
# Exemplo de uso no backend
@app.get("/admin/data")
async def get_admin_data(
    current_user: Dict = Depends(auth_manager.require_admin())
):
    # Apenas admins podem acessar
    pass

@app.get("/content/edit")
async def edit_content(
    current_user: Dict = Depends(auth_manager.require_permission("content"))
):
    # Apenas usuários com permissão 'content'
    pass
```

### Validações
- Email format validation
- Senha mínima 6 caracteres
- Role validation
- Token expiration handling

## 🛠️ Desenvolvimento

### Estrutura de Arquivos
```
backend/modules/auth_manager.py    # Sistema de auth backend
frontend/js/auth.js                # Auth frontend
frontend/js/dashboard.js           # Interface dashboard
frontend/js/app.js                 # Controlador principal
frontend/index.html                # Interface web
```

### Debugging
```javascript
// No console do browser
debug.auth()      // Info do auth manager
debug.user()      // Usuário atual
debug.dashboard() // Info do dashboard
debug.logout()    # Fazer logout
```

## 📊 Monitoramento

### Health Check
```bash
curl https://redacao.admin.recifemais.com.br/health
```

Resposta inclui status do sistema de auth:
```json
{
  "status": "healthy",
  "checks": {
    "auth": true,
    "database": true,
    "supabase": true,
    // ... outros serviços
  }
}
```

### Logs
- Todos os logins são logados
- Criação/edição de usuários registrada
- Erros de autenticação capturados

## 🚨 Troubleshooting

### Problemas Comuns

**1. "Token inválido ou expirado"**
- Solução: Fazer logout e login novamente
- Causa: Token expirou ou foi invalidado

**2. "Permissão negada"**
- Solução: Verificar role do usuário
- Causa: Usuário não tem permissão para a ação

**3. "Erro ao criar admin inicial"**
- Solução: Verificar se já existe admin
- Causa: Admin já foi criado anteriormente

**4. Frontend não carrega**
- Solução: Verificar console do browser
- Causa: Erro de JavaScript ou conexão

### Comandos Úteis

```bash
# Verificar status do sistema
curl https://redacao.admin.recifemais.com.br/health

# Testar login via API
curl -X POST https://redacao.admin.recifemais.com.br/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "seu@email.com", "password": "sua_senha"}'

# Listar usuários (com token admin)
curl https://redacao.admin.recifemais.com.br/admin/users \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 🔄 Próximos Passos

1. **Melhorar UI**: Adicionar toasts, modais mais elaborados
2. **Audit Log**: Registrar todas as ações dos usuários
3. **2FA**: Implementar autenticação de dois fatores
4. **Password Reset**: Sistema de recuperação de senha
5. **Profile Management**: Permitir usuários editarem perfil

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs do sistema
2. Consultar este guia
3. Testar endpoints via curl
4. Verificar console do browser (F12)

---

**Versão**: 2.4.0  
**Última atualização**: Dezembro 2024  
**Status**: ✅ Produção 