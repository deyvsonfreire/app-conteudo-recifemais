"""
Gerenciador de configurações seguras armazenadas no banco de dados
"""
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)

class SecureConfigManager:
    """Gerencia configurações seguras do banco de dados com cache"""
    
    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._db = None
    
    @property
    def db(self):
        """Lazy loading do database manager"""
        if self._db is None:
            from .database import db
            self._db = db
        return self._db
    
    def get(self, key: str, fallback: Optional[str] = None) -> Optional[str]:
        """
        Busca configuração segura com cache
        
        Args:
            key: Chave da configuração
            fallback: Valor padrão se não encontrar
            
        Returns:
            Valor da configuração ou fallback
        """
        try:
            # Verificar cache primeiro
            if key in self._cache:
                return self._cache[key]
            
            # Buscar no banco
            value = self.db.get_secure_config(key)
            
            if value:
                # Adicionar ao cache
                self._cache[key] = value
                return value
            
            return fallback
            
        except Exception as e:
            logger.error(f"Erro ao buscar configuração segura '{key}': {e}")
            return fallback
    
    def set(self, key: str, value: str, description: str = "") -> bool:
        """
        Define configuração segura
        
        Args:
            key: Chave da configuração
            value: Valor da configuração
            description: Descrição da configuração
            
        Returns:
            True se salvou com sucesso
        """
        try:
            result = self.db.set_secure_config(key, value, description)
            
            if result:
                # Atualizar cache
                self._cache[key] = value
                logger.info(f"Configuração segura '{key}' definida com sucesso")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao definir configuração segura '{key}': {e}")
            return False
    
    def clear_cache(self):
        """Limpa o cache de configurações"""
        self._cache.clear()
        logger.info("Cache de configurações seguras limpo")
    
    def get_all_keys(self) -> list:
        """Retorna todas as chaves de configuração disponíveis"""
        try:
            # Esta funcionalidade pode ser implementada se necessário
            # Por enquanto, retorna as chaves conhecidas
            return [
                "wordpress_username",
                "wordpress_password", 
                "gmail_client_id",
                "gmail_client_secret",
                "google_ai_api_key",
                "supabase_service_key"
            ]
        except Exception as e:
            logger.error(f"Erro ao listar chaves de configuração: {e}")
            return []

# Instância global
secure_config = SecureConfigManager()

# Funções de conveniência
def get_secure_config(key: str, fallback: Optional[str] = None) -> Optional[str]:
    """Função de conveniência para buscar configuração segura"""
    return secure_config.get(key, fallback)

def set_secure_config(key: str, value: str, description: str = "") -> bool:
    """Função de conveniência para definir configuração segura"""
    return secure_config.set(key, value, description) 