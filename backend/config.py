"""
Configurações da aplicação RecifeMais Conteúdo
"""
import os
import logging
from pydantic_settings import BaseSettings
from typing import Optional

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Configurações básicas
    APP_NAME: str = "RecifeMais Conteúdo"
    APP_VERSION: str = "2.5.1-SIMPLIFIED"  # Versão simplificada
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
    
    # ==========================================
    # CREDENCIAIS DIRETAS DO .ENV (SIMPLIFICADO)
    # ==========================================
    
    # Google AI (Gemini) - OBRIGATÓRIO
    GOOGLE_AI_API_KEY: str
    
    # Gmail OAuth - OBRIGATÓRIO
    GMAIL_CLIENT_ID: str
    GMAIL_CLIENT_SECRET: str
    
    # WordPress - OBRIGATÓRIO
    WORDPRESS_USERNAME: str
    WORDPRESS_PASSWORD: str
    
    # Google Data - OPCIONAL
    GSC_SITE_URL: Optional[str] = None
    GA4_PROPERTY_ID: Optional[str] = None
    
    # Meta/Facebook - OPCIONAL
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
        case_sensitive = True
    
    # ==========================================
    # PROPRIEDADES SIMPLIFICADAS (SEM SUPABASE)
    # ==========================================
    
    @property
    def secure_google_ai_api_key(self) -> str:
        """API Key do Google AI (Gemini) - DIRETO DO .ENV"""
        return self.GOOGLE_AI_API_KEY
    
    @property
    def secure_gmail_client_id(self) -> str:
        """Client ID OAuth Gmail - DIRETO DO .ENV"""
        return self.GMAIL_CLIENT_ID
    
    @property
    def secure_gmail_client_secret(self) -> str:
        """Client Secret OAuth Gmail - DIRETO DO .ENV"""
        return self.GMAIL_CLIENT_SECRET
    
    @property
    def secure_wordpress_username(self) -> str:
        """Username WordPress - DIRETO DO .ENV"""
        return self.WORDPRESS_USERNAME
    
    @property
    def secure_wordpress_password(self) -> str:
        """Password WordPress - DIRETO DO .ENV"""
        return self.WORDPRESS_PASSWORD
    
    @property
    def secure_gsc_site_url(self) -> Optional[str]:
        """URL do site no Google Search Console - DIRETO DO .ENV"""
        return self.GSC_SITE_URL
    
    @property
    def secure_ga4_property_id(self) -> Optional[str]:
        """Property ID do Google Analytics 4 - DIRETO DO .ENV"""
        return self.GA4_PROPERTY_ID
    
    @property
    def secure_facebook_app_id(self) -> Optional[str]:
        """ID do aplicativo Facebook - DIRETO DO .ENV"""
        return self.FACEBOOK_APP_ID
    
    @property
    def secure_facebook_app_secret(self) -> Optional[str]:
        """Chave secreta do aplicativo Facebook - DIRETO DO .ENV"""
        return self.FACEBOOK_APP_SECRET
    
    @property
    def secure_facebook_access_token(self) -> Optional[str]:
        """Token de acesso do Facebook - DIRETO DO .ENV"""
        return self.FACEBOOK_ACCESS_TOKEN
    
    @property
    def secure_instagram_account_id(self) -> Optional[str]:
        """ID da conta Instagram Business - DIRETO DO .ENV"""
        return self.INSTAGRAM_ACCOUNT_ID

    def validate_required_credentials(self) -> dict:
        """Valida se todas as credenciais obrigatórias estão presentes"""
        missing = []
        status = {}
        
        # Verificar credenciais obrigatórias
        required_creds = {
            "GOOGLE_AI_API_KEY": self.GOOGLE_AI_API_KEY,
            "GMAIL_CLIENT_ID": self.GMAIL_CLIENT_ID,
            "GMAIL_CLIENT_SECRET": self.GMAIL_CLIENT_SECRET,
            "WORDPRESS_USERNAME": self.WORDPRESS_USERNAME,
            "WORDPRESS_PASSWORD": self.WORDPRESS_PASSWORD,
            "SUPABASE_URL": self.SUPABASE_URL,
            "SUPABASE_ANON_KEY": self.SUPABASE_ANON_KEY,
            "SUPABASE_SERVICE_KEY": self.SUPABASE_SERVICE_KEY,
        }
        
        for key, value in required_creds.items():
            if not value or value.strip() == "":
                missing.append(key)
                status[key] = "❌ MISSING"
            else:
                status[key] = "✅ OK"
        
        # Verificar credenciais opcionais
        optional_creds = {
            "GSC_SITE_URL": self.GSC_SITE_URL,
            "GA4_PROPERTY_ID": self.GA4_PROPERTY_ID,
            "FACEBOOK_APP_ID": self.FACEBOOK_APP_ID,
        }
        
        for key, value in optional_creds.items():
            if value and value.strip():
                status[key] = "✅ OK (Optional)"
            else:
                status[key] = "⚠️ NOT SET (Optional)"
        
        return {
            "missing_required": missing,
            "total_missing": len(missing),
            "all_status": status,
            "is_valid": len(missing) == 0
        }

# Instância global das configurações
settings = Settings()

# Log de inicialização
logger.info(f"🔧 Configurações carregadas - Versão {settings.APP_VERSION}")
logger.info(f"📍 Ambiente: {settings.ENVIRONMENT}")
logger.info(f"🌐 Base URL: {settings.BASE_URL}")

# Validar credenciais na inicialização
try:
    validation = settings.validate_required_credentials()
    if validation["is_valid"]:
        logger.info("✅ Todas as credenciais obrigatórias estão presentes")
    else:
        logger.error(f"❌ Credenciais faltando: {validation['missing_required']}")
except Exception as e:
    logger.error(f"❌ Erro ao validar credenciais: {e}") 