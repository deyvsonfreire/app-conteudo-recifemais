#!/usr/bin/env python3
"""
Script para migrar credenciais sensíveis do arquivo .env para o banco de dados
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

# Importar módulos do backend
from backend.database import db
from backend.config import settings

def migrate_credentials():
    """Migra credenciais sensíveis para o banco de dados"""
    
    print("🔐 Iniciando migração de credenciais para o banco de dados...")
    
    # Credenciais sensíveis para migrar
    sensitive_configs = {
        "wordpress_username": {
            "value": settings.WORDPRESS_USERNAME,
            "description": "Usuário WordPress para API"
        },
        "wordpress_password": {
            "value": settings.WORDPRESS_PASSWORD,
            "description": "Senha WordPress para API"
        },
        "gmail_client_id": {
            "value": settings.GMAIL_CLIENT_ID,
            "description": "Client ID OAuth Gmail"
        },
        "gmail_client_secret": {
            "value": settings.GMAIL_CLIENT_SECRET,
            "description": "Client Secret OAuth Gmail"
        },
        "google_ai_api_key": {
            "value": settings.GOOGLE_AI_API_KEY,
            "description": "Chave API Google AI (Gemini)"
        },
        "supabase_service_key": {
            "value": settings.SUPABASE_SERVICE_KEY,
            "description": "Chave de serviço Supabase"
        }
    }
    
    success_count = 0
    total_count = len(sensitive_configs)
    
    for key, config in sensitive_configs.items():
        if config["value"]:
            try:
                result = db.set_secure_config(
                    key=key,
                    value=config["value"],
                    description=config["description"]
                )
                if result:
                    print(f"✅ {key}: Migrado com sucesso")
                    success_count += 1
                else:
                    print(f"❌ {key}: Falha na migração")
            except Exception as e:
                print(f"❌ {key}: Erro - {e}")
        else:
            print(f"⚠️ {key}: Valor vazio, pulando...")
    
    print(f"\n📊 Migração concluída: {success_count}/{total_count} credenciais migradas")
    
    if success_count == total_count:
        print("\n🎉 Todas as credenciais foram migradas com sucesso!")
        print("💡 Próximos passos:")
        print("1. Verifique se a aplicação está funcionando corretamente")
        print("2. Remova as credenciais sensíveis do arquivo .env")
        print("3. Adicione as credenciais removidas ao .gitignore")
    else:
        print(f"\n⚠️ Algumas credenciais não foram migradas. Verifique os erros acima.")

def verify_migration():
    """Verifica se as credenciais foram migradas corretamente"""
    
    print("\n🔍 Verificando migração...")
    
    keys_to_check = [
        "wordpress_username",
        "wordpress_password", 
        "gmail_client_id",
        "gmail_client_secret",
        "google_ai_api_key",
        "supabase_service_key"
    ]
    
    for key in keys_to_check:
        value = db.get_secure_config(key)
        if value:
            # Mostrar apenas os primeiros e últimos caracteres para segurança
            masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "****"
            print(f"✅ {key}: {masked_value}")
        else:
            print(f"❌ {key}: Não encontrado")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrar credenciais para banco de dados")
    parser.add_argument("--verify", action="store_true", help="Apenas verificar migração existente")
    
    args = parser.parse_args()
    
    if args.verify:
        verify_migration()
    else:
        migrate_credentials()
        verify_migration() 