"""
Conexão e utilitários do Supabase
"""
from supabase import create_client, Client
from .config import settings
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self):
        # Usar credencial segura com fallback
        service_key = settings.secure_supabase_service_key
        if not service_key:
            raise ValueError("SUPABASE_SERVICE_KEY não encontrada nem no banco nem no .env")
            
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            service_key
        )
    
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
            # Por enquanto, retorna lista vazia já que não temos embeddings no banco ainda
            # Em versões futuras, implementar busca por similaridade usando pgvector
            result = self.client.table("knowledge_base")\
                .select("*")\
                .limit(limit)\
                .execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Erro ao buscar conteúdo similar: {e}")
            return []

    def get_secure_config(self, key: str) -> Optional[str]:
        """Busca configuração segura/sensível"""
        try:
            result = self.client.table("secure_config").select("encrypted_value").eq("key", key).execute()
            if result.data:
                # Por enquanto retorna direto, mas em versão futura implementar decriptação
                return result.data[0]["encrypted_value"]
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar configuração segura: {e}")
            return None

    def set_secure_config(self, key: str, value: str, description: str = "") -> bool:
        """Define configuração segura/sensível"""
        try:
            # Por enquanto salva direto, mas em versão futura implementar criptografia
            data = {
                "key": key,
                "encrypted_value": value,
                "description": description,
                "updated_at": "now()"
            }
            result = self.client.table("secure_config").upsert(data).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Erro ao definir configuração segura: {e}")
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

# Instância global
db = SupabaseManager() 