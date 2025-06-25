"""
Módulo para configurações seguras sem dependência circular
"""
import os
from typing import Optional

def get_secure_config(key: str) -> Optional[str]:
    """
    Busca configuração segura do banco de dados
    
    Args:
        key: Nome da chave da configuração
        
    Returns:
        Valor da configuração ou None
    """
    try:
        # Import lazy para evitar dependência circular
        from supabase import create_client
        
        # Usar variáveis de ambiente diretamente para evitar circular import
        supabase_url = os.getenv("SUPABASE_URL", "https://aoyrpadrrsckxbuadcnf.supabase.co")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDgwNjkxOSwiZXhwIjoyMDY2MzgyOTE5fQ.EWx1wZZutcONrJYSzF2r1mvuav0KilXuPOOoWJYjAyc")
        
        if not supabase_key:
            return None
            
        client = create_client(supabase_url, supabase_key)
        
        result = client.table("secure_config").select("encrypted_value").eq("key", key).execute()
        
        if result.data:
            return result.data[0]["encrypted_value"]
        
        return None
        
    except Exception:
        # Se houver qualquer erro, retornar None
        # Isso permite que o sistema funcione mesmo sem o banco
        return None

def set_secure_config(key: str, value: str, description: str = "") -> bool:
    """
    Define configuração segura no banco de dados
    
    Args:
        key: Nome da chave
        value: Valor a ser armazenado
        description: Descrição da configuração
        
    Returns:
        True se sucesso, False caso contrário
    """
    try:
        # Import lazy para evitar dependência circular
        from supabase import create_client
        
        # Usar variáveis de ambiente diretamente
        supabase_url = os.getenv("SUPABASE_URL", "https://aoyrpadrrsckxbuadcnf.supabase.co")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFveXJwYWRycnNja3hidWFkY25mIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDgwNjkxOSwiZXhwIjoyMDY2MzgyOTE5fQ.EWx1wZZutcONrJYSzF2r1mvuav0KilXuPOOoWJYjAyc")
        
        if not supabase_key:
            return False
            
        client = create_client(supabase_url, supabase_key)
        
        data = {
            "key": key,
            "encrypted_value": value,
            "description": description,
            "updated_at": "now()"
        }
        
        result = client.table("secure_config").upsert(data).execute()
        return len(result.data) > 0
        
    except Exception:
        # Se houver qualquer erro, retornar False
        return False 