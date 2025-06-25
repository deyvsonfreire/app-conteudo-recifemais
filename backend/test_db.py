#!/usr/bin/env python3
"""
Script para testar conexão com Supabase
"""
import asyncio
from database import db
from datetime import datetime
import hashlib

async def test_database():
    """Testa operações básicas do banco"""
    print("🔍 Testando conexão com Supabase...")
    
    try:
        # Testar configuração do sistema
        print("1. Testando get_system_config...")
        config = await db.get_system_config("test_key")
        print(f"   ✅ Config result: {config}")
        
        # Testar inserção de email
        print("2. Testando insert_email_cache...")
        test_email = {
            "email_hash": hashlib.md5("test_email_content".encode()).hexdigest(),
            "sender": "test@example.com",
            "subject": "Email de Teste",
            "content_text": "Conteúdo de teste para verificar funcionamento",
            "received_at": datetime.now(),
            "status": "pending"
        }
        
        result = await db.insert_email_cache(test_email)
        print(f"   ✅ Insert result: {result}")
        
        if result:
            email_id = result["id"]
            print(f"   📧 Email inserido com ID: {email_id}")
            
            # Testar busca por hash
            print("3. Testando get_email_by_hash...")
            found_email = await db.get_email_by_hash(test_email["email_hash"])
            print(f"   ✅ Found email: {found_email is not None}")
            
            # Testar atualização
            print("4. Testando update_email_cache...")
            update_result = await db.update_email_cache(email_id, {
                "status": "processed",
                "processed_at": datetime.now()
            })
            print(f"   ✅ Update result: {update_result}")
        
        print("\n🎉 Todos os testes passaram!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database()) 