"""
Configurações da aplicação RecifeMais Conteúdo
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Configurações gerais
    APP_NAME: str = "RecifeMais Conteúdo"
    APP_VERSION: str = "2.3.0"
    DEBUG: bool = False
    
    # URLs e Endpoints - PRODUÇÃO
    WORDPRESS_URL: str = "https://recifemais.com.br"
    GMAIL_REDIRECT_URI: str = "https://redacao.admin.recifemais.com.br/auth/callback"
    BASE_URL: str = "https://redacao.admin.recifemais.com.br"
    
    # Configurações Google Data (Search Console + Analytics)
    GSC_SITE_URL: str = "https://recifemais.com.br/"
    GA4_PROPERTY_ID: str = ""  # Será configurado via admin
    
    # Supabase - URLs públicos
    SUPABASE_URL: str = "https://aoyrpadrrsckxbuadcnf.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MDY5MTksImV4cCI6MjA2NjM4MjkxOX0.BAkMkcWzUeLL9_G-qAEdOX-Nhjmr5WLSv_AOqvdxA74"
    
    # Credenciais sensíveis (fallback do .env, mas prioriza banco de dados)
    GOOGLE_AI_API_KEY: Optional[str] = None
    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None
    WORDPRESS_USERNAME: Optional[str] = None
    WORDPRESS_PASSWORD: Optional[str] = None
    
    # SUPABASE_SERVICE_KEY - temporariamente no .env para evitar dependência circular
    SUPABASE_SERVICE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDgwNjkxOSwiZXhwIjoyMDY2MzgyOTE5fQ.EWx1wZZutcONrJYSzF2r1mvuav0KilXuPOOoWJYjAyc"
    
    # Cache Redis (para desenvolvimento local)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Configurações de IA
    MAX_TOKENS_PER_REQUEST: int = 8000
    EMBEDDING_MODEL: str = "text-embedding-004"
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    
    # Configurações de processamento
    EMAIL_CHECK_INTERVAL: int = 300  # 5 minutos
    MAX_EMAILS_PER_BATCH: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignorar campos extras do .env
    
    def get_secure_credential(self, key: str) -> Optional[str]:
        """
        Busca credencial segura do banco de dados com fallback para .env
        
        Args:
            key: Nome da chave da credencial
            
        Returns:
            Valor da credencial ou None
        """
        try:
            from .secure_config import get_secure_config
            
            # Tentar buscar do banco primeiro
            value = get_secure_config(key)
            if value:
                return value
            
            # Fallback para valor do .env
            env_value = getattr(self, key.upper(), None)
            return env_value
            
        except Exception:
            # Se houver erro, usar valor do .env
            return getattr(self, key.upper(), None)
    
    @property
    def secure_google_ai_api_key(self) -> Optional[str]:
        """Chave API Google AI (do banco ou .env)"""
        return self.get_secure_credential("google_ai_api_key") or self.GOOGLE_AI_API_KEY
    
    @property
    def secure_gmail_client_id(self) -> Optional[str]:
        """Client ID Gmail (do banco ou .env)"""
        return self.get_secure_credential("gmail_client_id") or self.GMAIL_CLIENT_ID
    
    @property
    def secure_gmail_client_secret(self) -> Optional[str]:
        """Client Secret Gmail (do banco ou .env)"""
        return self.get_secure_credential("gmail_client_secret") or self.GMAIL_CLIENT_SECRET
    
    @property
    def secure_wordpress_username(self) -> Optional[str]:
        """Username WordPress (do banco ou .env)"""
        return self.get_secure_credential("wordpress_username") or self.WORDPRESS_USERNAME
    
    @property
    def secure_wordpress_password(self) -> Optional[str]:
        """Password WordPress (do banco ou .env)"""
        return self.get_secure_credential("wordpress_password") or self.WORDPRESS_PASSWORD
    
    @property
    def secure_supabase_service_key(self) -> Optional[str]:
        """Service Key Supabase (do banco ou .env)"""
        return self.get_secure_credential("supabase_service_key") or self.SUPABASE_SERVICE_KEY
    
    @property
    def secure_gsc_site_url(self) -> str:
        """URL do site no Google Search Console"""
        return self.get_secure_credential("gsc_site_url") or self.GSC_SITE_URL
    
    @property
    def secure_ga4_property_id(self) -> Optional[str]:
        """Property ID do Google Analytics 4"""
        return self.get_secure_credential("ga4_property_id") or self.GA4_PROPERTY_ID

# Instância global das configurações
settings = Settings() 