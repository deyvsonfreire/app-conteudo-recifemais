"""
Configurações da aplicação RecifeMais Conteúdo
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Configurações básicas
    APP_NAME: str = "RecifeMais Conteúdo"
    APP_VERSION: str = "2.5.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    PORT: int = 8001
    
    # URLs
    BASE_URL: str = "http://localhost:8001"
    WORDPRESS_URL: str = "https://recifemais.com.br"
    GMAIL_REDIRECT_URI: str = "http://localhost:8001/auth/callback"
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # Google AI (Gemini) - PRIORIDADE 1
    GOOGLE_AI_API_KEY: Optional[str] = None
    
    # Gmail OAuth - PRIORIDADE 1
    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None
    
    # Google Data - PRIORIDADE 2
    GSC_SITE_URL: Optional[str] = None
    GA4_PROPERTY_ID: Optional[str] = None
    
    # WordPress
    WORDPRESS_USERNAME: Optional[str] = None
    WORDPRESS_PASSWORD: Optional[str] = None
    
    # ===========================================
    # META/FACEBOOK INTEGRATION
    # ===========================================
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_ACCESS_TOKEN: Optional[str] = None
    INSTAGRAM_ACCOUNT_ID: Optional[str] = None
    
    # IA Configurations
    MAX_TOKENS_PER_REQUEST: int = 8000
    EMBEDDING_MODEL: str = "text-embedding-004"
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    
    # Processing
    EMAIL_CHECK_INTERVAL: int = 300
    MAX_EMAILS_PER_BATCH: int = 10
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379"
    
    # Logs
    LOG_LEVEL: str = "INFO"
    
    # Performance
    HTTP_TIMEOUT: int = 30
    CACHE_TTL: int = 3600
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8001"
    
    # Feature Flags
    ENABLE_GOOGLE_DATA_INTEGRATION: bool = True
    ENABLE_WORDPRESS_PUBLISHING: bool = True
    ENABLE_EMAIL_PROCESSING: bool = True
    ENABLE_USER_MANAGEMENT: bool = True
    ENABLE_ANALYTICS_DASHBOARD: bool = True
    ENABLE_META_INTEGRATION: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Tentar carregar de múltiplos arquivos de configuração
        env_files = [".env", "config.local.env", "config.prod.env"]
    
    def get_secure_credential(self, key: str) -> Optional[str]:
        """
        Busca credencial segura do banco de dados com fallback para .env
        
        Args:
            key: Nome da chave da credencial
            
        Returns:
            Valor da credencial ou None
        """
        try:
            # Import lazy para evitar dependência circular
            from .secure_config import get_secure_config
            
            # Tentar buscar do banco primeiro
            value = get_secure_config(key)
            if value:
                return value
            
            # Fallback para valor do .env
            env_value = getattr(self, key.upper(), None)
            return env_value
            
        except Exception:
            # Se houver erro (circular import, etc), usar valor do .env
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
    
    @property
    def secure_facebook_app_id(self) -> Optional[str]:
        """ID do aplicativo Facebook"""
        return self.get_secure_credential("facebook_app_id") or self.FACEBOOK_APP_ID
    
    @property
    def secure_facebook_app_secret(self) -> Optional[str]:
        """Chave secreta do aplicativo Facebook"""
        return self.get_secure_credential("facebook_app_secret") or self.FACEBOOK_APP_SECRET
    
    @property
    def secure_facebook_access_token(self) -> Optional[str]:
        """Token de acesso do Facebook"""
        return self.get_secure_credential("facebook_access_token") or self.FACEBOOK_ACCESS_TOKEN
    
    @property
    def secure_instagram_account_id(self) -> Optional[str]:
        """ID da conta Instagram Business"""
        return self.get_secure_credential("instagram_account_id") or self.INSTAGRAM_ACCOUNT_ID

# Instância global das configurações
settings = Settings() 