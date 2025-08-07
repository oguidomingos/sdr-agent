#!/usr/bin/env python3
"""Test direct message insertion to validate the fix"""

from supabase import create_client
from datetime import datetime

def test_direct_insert():
    """Test inserting a message directly to verify schema compatibility"""
    print("🧪 TESTANDO INSERÇÃO DIRETA DE MENSAGEM")
    print("=" * 50)
    
    try:
        # Connect to Supabase
        supabase_url = 'https://roezccmxctqbvdjlgdru.supabase.co'
        service_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDA3ODUzNSwiZXhwIjoyMDY5NjU0NTM1fQ.sE5v5FCfMKhsnehtnCF75S1N41g7f3JaZS1v1sDCeU0'
        
        supabase = create_client(supabase_url, service_key)
        client_id = "77f276b5-5a0a-4888-be96-5ab3fa96b1b3"
        
        # Test the new fixed structure
        message_data = {
            "client_id": client_id,
            "user_id": "5561936180578@s.whatsapp.net",
            "user_name": "Test User",
            "message_direction": "inbound",
            "content": "Test message for schema validation",
            "message_metadata": {},
            "status": "none",
            "lead_score": 0
        }
        
        print("📝 Tentando inserir mensagem com nova estrutura...")
        print(f"Dados: {message_data}")
        
        result = supabase.table('messages').insert(message_data).execute()
        
        if result.data:
            print(f"✅ Inserção bem-sucedida! ID da mensagem: {result.data[0]['id']}")
            print(f"Timestamp criado: {result.data[0]['timestamp']}")
            return True
        else:
            print("❌ Inserção retornou dados vazios")
            return False
            
    except Exception as e:
        print(f"❌ Erro na inserção: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False

def test_old_structure():
    """Test with the old structure to compare"""
    print("\n🧪 TESTANDO ESTRUTURA ANTIGA (PARA COMPARAÇÃO)")
    print("=" * 50)
    
    try:
        supabase_url = 'https://roezccmxctqbvdjlgdru.supabase.co'
        service_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDA3ODUzNSwiZXhwIjoyMDY5NjU0NTM1fQ.sE5v5FCfMKhsnehtnCF75S1N41g7f3JaZS1v1sDCeU0'
        
        supabase = create_client(supabase_url, service_key)
        client_id = "77f276b5-5a0a-4888-be96-5ab3fa96b1b3"
        
        # Test the old problematic structure
        message_data_old = {
            "client_id": client_id,
            "user_id": "5561936180578@s.whatsapp.net",
            "message_direction": "inbound",
            "content": "Test message old structure",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "none",
            "lead_score": 0
        }
        
        print("📝 Tentando inserir mensagem com estrutura antiga...")
        print(f"Dados: {message_data_old}")
        
        result = supabase.table('messages').insert(message_data_old).execute()
        
        if result.data:
            print(f"✅ Inserção antiga bem-sucedida (inesperado)!")
            return True
        else:
            print("❌ Inserção antiga falhou conforme esperado")
            return False
            
    except Exception as e:
        print(f"❌ Erro na inserção antiga: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("🚀 TESTANDO CORREÇÃO DA INSERÇÃO DE MENSAGENS")
    print("=" * 60)
    
    # Test new fixed structure
    new_success = test_direct_insert()
    
    # Test old structure for comparison
    old_success = test_old_structure()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"✅ Nova estrutura: {'PASSOU' if new_success else '❌ FALHOU'}")
    print(f"✅ Estrutura antiga: {'PASSOU' if old_success else '❌ FALHOU'}")
    
    if new_success and not old_success:
        print("\n🎉 CORREÇÃO BEM-SUCEDIDA!")
        print("A nova estrutura funciona enquanto a antiga falha.")
    elif new_success and old_success:
        print("\n⚠️ AMBAS FUNCIONAM - Possível problema em outro lugar")
    elif not new_success and not old_success:
        print("\n❌ AMBAS FALHARAM - Problema mais profundo")
    else:
        print("\n🤔 RESULTADO INESPERADO - Revisar implementação")