"""
Conexão e utilitários do Supabase
"""
from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

# Import com fallback para desenvolvimento e produção
try:
    from .config import settings
except ImportError:
    from config import settings

logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self):
        # Usar credencial do .env primeiro (para evitar dependência circular)
        service_key = settings.SUPABASE_SERVICE_KEY
        
        # Se não tiver no .env, tentar buscar do banco (lazy loading)
        if not service_key:
            service_key = self._get_service_key_from_env_or_fail()
            
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            service_key
        )
        
    def _get_service_key_from_env_or_fail(self):
        """Busca service key do .env ou falha"""
        # Para produção, a chave deve estar no .env temporariamente
        # até a migração ser concluída
        import os
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not key:
            raise ValueError("SUPABASE_SERVICE_KEY não encontrada no .env. Adicione temporariamente para migração.")
        return key
    
    def insert_email_cache(self, email_data: Dict[str, Any]) -> Optional[Dict]:
        """Insere um email no cache"""
        try:
            # Converter datetime para string ISO se necessário
            processed_data = email_data.copy()
            for key, value in processed_data.items():
                if hasattr(value, 'isoformat'):  # datetime object
                    processed_data[key] = value.isoformat()
            
            result = self.client.table("email_cache").insert(processed_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Erro ao inserir email cache: {e}")
            return None
    
    def get_email_by_hash(self, email_hash: str) -> Optional[Dict]:
        """Busca email pelo hash"""
        try:
            result = self.client.table("email_cache").select("*").eq("email_hash", email_hash).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar email: {e}")
            return None
    
    def update_email_cache(self, email_id: str, update_data: Dict[str, Any]) -> bool:
        """Atualiza dados do email cache"""
        try:
            # Converter datetime para string ISO se necessário
            processed_data = update_data.copy()
            for key, value in processed_data.items():
                if hasattr(value, 'isoformat'):  # datetime object
                    processed_data[key] = value.isoformat()
            
            result = self.client.table("email_cache").update(processed_data).eq("id", email_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Erro ao atualizar email: {e}")
            return False
    
    def get_pending_emails(self, limit: int = 10) -> List[Dict]:
        """Busca emails pendentes de processamento"""
        try:
            result = self.client.table("email_cache")\
                .select("*")\
                .eq("status", "pending")\
                .order("received_at", desc=False)\
                .limit(limit)\
                .execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Erro ao buscar emails pendentes: {e}")
            return []
    
    def get_all_emails(self, limit: int = 50) -> List[Dict]:
        """Busca todos os emails processados"""
        try:
            result = self.client.table("email_cache")\
                .select("*")\
                .order("received_at", desc=True)\
                .limit(limit)\
                .execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Erro ao buscar emails: {e}")
            return []
    
    def get_system_config(self, key: str) -> Optional[Any]:
        """Busca configuração do sistema"""
        try:
            result = self.client.table("system_config").select("value").eq("key", key).execute()
            return result.data[0]["value"] if result.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar configuração: {e}")
            return None

    def set_system_config(self, key: str, value: Any, description: str = "") -> bool:
        """Define configuração do sistema"""
        try:
            data = {"key": key, "value": value, "description": description}
            result = self.client.table("system_config").upsert(data).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Erro ao definir configuração: {e}")
            return False

    def search_similar_content(self, embedding: List[float], limit: int = 5) -> List[Dict]:
        """Busca conteúdo similar usando embeddings (RAG)"""
        try:
            # Converter embedding para formato compatível com pgvector
            embedding_str = f"[{','.join(map(str, embedding))}]"
            
            # CORREÇÃO: Chamar RPC diretamente no client, não na table
            result = self.client.rpc("match_documents", {
                "query_embedding": embedding_str,
                "match_threshold": 0.7,
                "match_count": limit
            }).execute()
            
            if result.data:
                return result.data
            
            # Fallback: busca simples por tópico se não tiver função RPC ou dados
            logger.warning("Função match_documents retornou vazio, usando busca simples")
            result = self.client.table("knowledge_base")\
                .select("content_text, source_url, topic, category_recifemais, metadata")\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Erro na busca de conteúdo similar: {e}")
            return []

    def get_secure_config(self, key: str) -> Optional[str]:
        """Obter configuração segura do banco de dados"""
        try:
            response = self.client.table("secure_config").select("encrypted_value").eq("key", key).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]["encrypted_value"]
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao obter configuração segura {key}: {e}")
            return None

    def set_secure_config(self, key: str, value: str, description: str = None) -> bool:
        """Definir configuração segura no banco de dados"""
        try:
            # Verificar se já existe
            existing = self.client.table("secure_config").select("id").eq("key", key).execute()
            
            data = {
                "key": key,
                "encrypted_value": value,
                "description": description or f"Configuração {key}",
                "updated_at": datetime.now().isoformat()
            }
            
            if existing.data:
                # Atualizar existente
                response = self.client.table("secure_config").update(data).eq("key", key).execute()
            else:
                # Criar novo
                data["created_at"] = datetime.now().isoformat()
                response = self.client.table("secure_config").insert(data).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração segura {key}: {e}")
            return False

    def list_secure_configs(self) -> List[Dict]:
        """Listar todas as configurações seguras (sem valores)"""
        try:
            response = self.client.table("secure_config").select("key, description, created_at, updated_at").execute()
            return response.data or []
            
        except Exception as e:
            logger.error(f"Erro ao listar configurações seguras: {e}")
            return []

    def delete_secure_config(self, key: str) -> bool:
        """Deletar configuração segura"""
        try:
            response = self.client.table("secure_config").delete().eq("key", key).execute()
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Erro ao deletar configuração segura {key}: {e}")
            return False

    def store_gmail_credentials(self, credentials_data: Dict[str, Any]) -> bool:
        """Armazena credenciais OAuth do Gmail de forma persistente"""
        try:
            import json
            # Converter credenciais para JSON
            creds_json = json.dumps(credentials_data)
            return self.set_secure_config("gmail_oauth_credentials", creds_json, "Credenciais OAuth Gmail")
        except Exception as e:
            logger.error(f"Erro ao armazenar credenciais Gmail: {e}")
            return False

    def get_gmail_credentials(self) -> Optional[Dict[str, Any]]:
        """Recupera credenciais OAuth do Gmail"""
        try:
            import json
            creds_json = self.get_secure_config("gmail_oauth_credentials")
            if creds_json:
                return json.loads(creds_json)
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar credenciais Gmail: {e}")
            return None

    def upgrade_to_secure_credentials(self):
        """Migra credenciais do .env para o banco de dados"""
        try:
            # Migrar credenciais sensíveis do .env para o banco
            credentials_to_migrate = [
                "google_ai_api_key",
                "gmail_client_id", 
                "gmail_client_secret",
                "wordpress_username",
                "wordpress_password"
            ]
            
            migrated = 0
            for cred_key in credentials_to_migrate:
                # Buscar valor do .env
                env_value = getattr(settings, cred_key.upper(), None)
                if env_value:
                    # Salvar no banco
                    if self.set_secure_config(cred_key, env_value, f"Migrado do .env - {cred_key}"):
                        migrated += 1
                        logger.info(f"Credencial {cred_key} migrada com sucesso")
            
            logger.info(f"Migração concluída: {migrated} credenciais migradas")
            return migrated > 0
            
        except Exception as e:
            logger.error(f"Erro na migração de credenciais: {e}")
            return False

# Instância global
db = SupabaseManager() 