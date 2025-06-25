"""
Configurações da aplicação RecifeMais Conteúdo
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Configurações gerais
    APP_NAME: str = "RecifeMais Conteúdo"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # APIs Google
    GOOGLE_AI_API_KEY: str = "AIzaSyBuPRxQo9lQEcyLVovTT-VSZAvl-b5i0U4"
    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None
    GMAIL_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    
    # WordPress
    WORDPRESS_URL: str = "https://v25.recifemais.com.br"
    WORDPRESS_USERNAME: str = "contato@recifemais.com.br"
    WORDPRESS_PASSWORD: str = "4DpP hCyj yUfh SRIb v84g fmed"
    
    # Supabase - Projeto correto
    SUPABASE_URL: str = "https://aoyrpadrrsckxbuadcnf.supabase.co"
    SUPABASE_ANON_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MDY5MTksImV4cCI6MjA2NjM4MjkxOX0.BAkMkcWzUeLL9_G-qAEdOX-Nhjmr5WLSv_AOqvdxA74"
    SUPABASE_SERVICE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDgwNjkxOSwiZXhwIjoyMDY2MzgyOTE5fQ.EWx1wZZutcONrJYSzF2r1mvuav0KilXuPOOoWJYjAyc"
    
    # Cache Redis (para desenvolvimento local)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Configurações de IA
    MAX_TOKENS_PER_REQUEST: int = 8000
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    
    # Configurações de processamento
    EMAIL_CHECK_INTERVAL: int = 300  # 5 minutos
    MAX_EMAILS_PER_BATCH: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignorar campos extras do .env

# Instância global das configurações
settings = Settings() 