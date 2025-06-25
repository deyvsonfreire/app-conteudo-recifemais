"""
Auth Manager - Sistema de Autenticação com Supabase Auth
Gerencia usuários, sessões e controle de acesso
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Supabase imports
from supabase import create_client, Client
from gotrue.errors import AuthApiError

# Internal imports
from ..config import settings
from ..database import db

logger = logging.getLogger(__name__)

# Security scheme para JWT
security = HTTPBearer()

class AuthManager:
    """
    Gerenciador de autenticação com Supabase Auth
    Controla usuários, sessões e permissões
    """
    
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.secure_supabase_service_key or settings.SUPABASE_SERVICE_KEY
        )
        self.roles = {
            'admin': ['*'],  # Acesso total
            'editor': ['content', 'analytics', 'wordpress'],  # Gestão de conteúdo
            'viewer': ['analytics', 'reports']  # Somente leitura
        }
        logger.info("🔐 Auth Manager inicializado")
    
    # ==========================================
    # USER MANAGEMENT
    # ==========================================
    
    def create_user(self, email: str, password: str, role: str = 'viewer', metadata: Dict = None) -> Dict:
        """
        Cria novo usuário no Supabase Auth
        
        Args:
            email: Email do usuário
            password: Senha inicial
            role: Papel do usuário (admin, editor, viewer)
            metadata: Dados adicionais do usuário
        """
        try:
            if role not in self.roles:
                raise ValueError(f"Role '{role}' não é válido. Use: {list(self.roles.keys())}")
            
            # Criar usuário no Supabase Auth
            response = self.supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,  # Auto-confirmar email em produção
                "user_metadata": {
                    "role": role,
                    "created_by": "system",
                    "created_at": datetime.now().isoformat(),
                    **(metadata or {})
                }
            })
            
            if response.user:
                logger.info(f"👤 Usuário criado: {email} (role: {role})")
                return {
                    "success": True,
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "role": role,
                    "message": "Usuário criado com sucesso"
                }
            else:
                raise Exception("Falha ao criar usuário")
                
        except AuthApiError as e:
            logger.error(f"Erro Supabase Auth ao criar usuário: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao criar usuário"
            }
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno ao criar usuário"
            }
    
    def list_users(self) -> List[Dict]:
        """Lista todos os usuários do sistema"""
        try:
            response = self.supabase.auth.admin.list_users()
            
            users = []
            # A resposta pode ser um objeto com atributo 'users' ou uma lista direta
            user_list = response.users if hasattr(response, 'users') else response
            
            for user in user_list:
                user_data = {
                    "id": user.id,
                    "email": user.email,
                    "role": user.user_metadata.get("role", "viewer") if user.user_metadata else "viewer",
                    "created_at": user.created_at,
                    "last_sign_in": user.last_sign_in_at,
                    "email_confirmed": user.email_confirmed_at is not None,
                    "is_active": not user.banned_until if hasattr(user, 'banned_until') else True
                }
                users.append(user_data)
            
            logger.info(f"📋 Listados {len(users)} usuários")
            return users
            
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            return []
    
    def update_user_role(self, user_id: str, new_role: str) -> Dict:
        """Atualiza o papel de um usuário"""
        try:
            if new_role not in self.roles:
                raise ValueError(f"Role '{new_role}' não é válido")
            
            response = self.supabase.auth.admin.update_user_by_id(
                user_id,
                {
                    "user_metadata": {
                        "role": new_role,
                        "updated_at": datetime.now().isoformat()
                    }
                }
            )
            
            if response.user:
                logger.info(f"🔄 Role atualizado: {response.user.email} -> {new_role}")
                return {
                    "success": True,
                    "message": f"Role atualizado para {new_role}"
                }
            else:
                raise Exception("Falha ao atualizar usuário")
                
        except Exception as e:
            logger.error(f"Erro ao atualizar role: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_user(self, user_id: str) -> Dict:
        """Remove um usuário do sistema"""
        try:
            response = self.supabase.auth.admin.delete_user(user_id)
            
            logger.info(f"🗑️ Usuário removido: {user_id}")
            return {
                "success": True,
                "message": "Usuário removido com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro ao remover usuário: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==========================================
    # AUTHENTICATION
    # ==========================================
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """
        Autentica usuário e retorna token JWT
        
        Args:
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            Dict com token, user info e permissões
        """
        try:
            # Autenticar com Supabase
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                user_role = response.user.user_metadata.get("role", "viewer")
                permissions = self.roles.get(user_role, [])
                
                logger.info(f"🔓 Login realizado: {email} (role: {user_role})")
                
                return {
                    "success": True,
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "role": user_role,
                        "permissions": permissions
                    },
                    "message": "Login realizado com sucesso"
                }
            else:
                raise Exception("Credenciais inválidas")
                
        except AuthApiError as e:
            logger.error(f"Erro de autenticação: {e}")
            return {
                "success": False,
                "error": "Credenciais inválidas",
                "message": "Email ou senha incorretos"
            }
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno de autenticação"
            }
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """Renova token de acesso usando refresh token"""
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if response.session:
                logger.info("🔄 Token renovado com sucesso")
                return {
                    "success": True,
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at
                }
            else:
                raise Exception("Falha ao renovar token")
                
        except Exception as e:
            logger.error(f"Erro ao renovar token: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def logout_user(self, access_token: str) -> Dict:
        """Faz logout do usuário invalidando o token"""
        try:
            # Definir token para a sessão atual
            self.supabase.auth.set_session(access_token, "")
            
            # Fazer logout
            self.supabase.auth.sign_out()
            
            logger.info("🔒 Logout realizado")
            return {
                "success": True,
                "message": "Logout realizado com sucesso"
            }
            
        except Exception as e:
            logger.error(f"Erro no logout: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==========================================
    # TOKEN VALIDATION
    # ==========================================
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verifica e decodifica token JWT do Supabase
        
        Args:
            token: JWT token do Supabase
            
        Returns:
            Dados do usuário se token válido, None se inválido
        """
        try:
            # Verificar token com Supabase
            response = self.supabase.auth.get_user(token)
            
            if response.user:
                user_role = response.user.user_metadata.get("role", "viewer")
                permissions = self.roles.get(user_role, [])
                
                return {
                    "user_id": response.user.id,
                    "email": response.user.email,
                    "role": user_role,
                    "permissions": permissions,
                    "is_authenticated": True
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Erro ao verificar token: {e}")
            return None
    
    def check_permission(self, user_permissions: List[str], required_permission: str) -> bool:
        """
        Verifica se usuário tem permissão específica
        
        Args:
            user_permissions: Lista de permissões do usuário
            required_permission: Permissão necessária
            
        Returns:
            True se tem permissão, False caso contrário
        """
        # Admin tem acesso total
        if '*' in user_permissions:
            return True
        
        # Verificar permissão específica
        return required_permission in user_permissions
    
    # ==========================================
    # MIDDLEWARE DEPENDENCIES
    # ==========================================
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
        """
        Dependency para obter usuário atual autenticado
        Usado como dependência no FastAPI
        """
        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="Token de autorização necessário",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user_data = self.verify_token(credentials.credentials)
        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Token inválido ou expirado",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user_data
    
    def require_permission(self, permission: str):
        """
        Dependency factory para exigir permissão específica
        
        Args:
            permission: Permissão necessária
            
        Returns:
            Dependency function
        """
        def permission_dependency(current_user: Dict = Depends(self.get_current_user)) -> Dict:
            if not self.check_permission(current_user.get("permissions", []), permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permissão '{permission}' necessária"
                )
            return current_user
        
        return permission_dependency
    
    def require_admin(self) -> callable:
        """Dependency para exigir permissão de admin"""
        def admin_dependency(current_user: Dict = Depends(self.get_current_user)) -> Dict:
            if current_user.get("role") != "admin":
                raise HTTPException(
                    status_code=403,
                    detail="Acesso restrito a administradores"
                )
            return current_user
        
        return admin_dependency
    
    # ==========================================
    # SYSTEM MANAGEMENT
    # ==========================================
    
    def get_auth_stats(self) -> Dict:
        """Retorna estatísticas do sistema de autenticação"""
        try:
            users = self.list_users()
            
            stats = {
                "total_users": len(users),
                "users_by_role": {},
                "active_users": 0,
                "recent_logins": 0
            }
            
            # Contar por role
            for user in users:
                role = user.get("role", "viewer")
                stats["users_by_role"][role] = stats["users_by_role"].get(role, 0) + 1
                
                if user.get("is_active"):
                    stats["active_users"] += 1
                
                # Login nos últimos 7 dias
                if user.get("last_sign_in"):
                    try:
                        last_sign_in = user["last_sign_in"]
                        # Converter string para datetime se necessário
                        if isinstance(last_sign_in, str):
                            last_login = datetime.fromisoformat(last_sign_in.replace('Z', '+00:00'))
                        else:
                            last_login = last_sign_in
                        
                        if last_login > datetime.now().replace(tzinfo=last_login.tzinfo) - timedelta(days=7):
                            stats["recent_logins"] += 1
                    except (ValueError, TypeError):
                        # Ignorar se não conseguir converter a data
                        pass
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de auth: {e}")
            return {}
    
    def create_initial_admin(self, email: str, password: str) -> Dict:
        """
        Cria usuário admin inicial do sistema
        Usado apenas na configuração inicial
        """
        try:
            # Verificar se já existe admin
            users = self.list_users()
            admin_exists = any(user.get("role") == "admin" for user in users)
            
            if admin_exists:
                return {
                    "success": False,
                    "message": "Admin já existe no sistema"
                }
            
            # Criar admin
            result = self.create_user(
                email=email,
                password=password,
                role="admin",
                metadata={
                    "name": "Administrador",
                    "initial_admin": True
                }
            )
            
            if result["success"]:
                logger.info(f"👑 Admin inicial criado: {email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao criar admin inicial: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Instância global
auth_manager = AuthManager() 