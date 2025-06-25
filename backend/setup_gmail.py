#!/usr/bin/env python3
"""
Script para configurar credenciais Gmail OAuth
"""
import os
import json
from config import settings

def setup_gmail_credentials():
    """Guia de configuração das credenciais Gmail"""
    
    print("🔧 CONFIGURAÇÃO GMAIL OAUTH - RecifeMais Conteúdo")
    print("=" * 60)
    
    print("\n📋 PASSO 1: Google Cloud Console")
    print("1. Acesse: https://console.cloud.google.com/")
    print("2. Crie um novo projeto ou selecione um existente")
    print("3. Ative a Gmail API:")
    print("   - Vá em 'APIs & Services' > 'Library'")
    print("   - Busque por 'Gmail API' e clique em 'Enable'")
    
    print("\n🔑 PASSO 2: Credenciais OAuth")
    print("1. Vá em 'APIs & Services' > 'Credentials'")
    print("2. Clique em '+ CREATE CREDENTIALS' > 'OAuth client ID'")
    print("3. Escolha 'Web application'")
    print("4. Configure:")
    print("   - Name: RecifeMais Gmail Integration")
    print("   - Authorized redirect URIs: http://localhost:8000/auth/callback")
    print("5. Baixe o arquivo JSON das credenciais")
    
    print("\n⚙️ PASSO 3: Configurar variáveis de ambiente")
    print("Adicione no seu arquivo .env:")
    print("GMAIL_CLIENT_ID=seu_client_id_aqui")
    print("GMAIL_CLIENT_SECRET=seu_client_secret_aqui")
    
    print("\n🚀 PASSO 4: Teste a configuração")
    print("1. Reinicie o servidor: python -m uvicorn main:app --reload")
    print("2. Acesse: http://localhost:8000/auth/gmail")
    print("3. Siga o processo de autorização")
    print("4. Teste: http://localhost:8000/gmail/status")
    
    print("\n" + "=" * 60)
    
    # Verificar se as credenciais estão configuradas
    if settings.GMAIL_CLIENT_ID and settings.GMAIL_CLIENT_SECRET:
        print("✅ Credenciais encontradas no .env!")
        print(f"Client ID: {settings.GMAIL_CLIENT_ID[:20]}...")
        print("Agora você pode testar a autenticação.")
    else:
        print("⚠️ Credenciais não encontradas no .env")
        print("Configure GMAIL_CLIENT_ID e GMAIL_CLIENT_SECRET primeiro.")
    
    print("\n📚 Documentação completa:")
    print("https://developers.google.com/gmail/api/quickstart/python")

def create_example_env():
    """Cria arquivo de exemplo com as configurações necessárias"""
    
    example_content = """# Gmail OAuth Credentials
GMAIL_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your_client_secret_here

# Exemplo de configuração completa:
# 1. Vá no Google Cloud Console
# 2. Crie credenciais OAuth 2.0
# 3. Configure redirect URI: http://localhost:8000/auth/callback
# 4. Cole as credenciais aqui
# 5. Reinicie o servidor
"""
    
    with open("gmail_env_example.txt", "w") as f:
        f.write(example_content)
    
    print("📄 Arquivo 'gmail_env_example.txt' criado!")

if __name__ == "__main__":
    setup_gmail_credentials()
    create_example_env() 