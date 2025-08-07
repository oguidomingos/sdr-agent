#!/usr/bin/env python3
"""Debug the exact status error that's happening in production"""

import sys
import os
sys.path.append('/Users/oguidomingos/sdr-agent')

from api.index import save_message_to_database

def test_exact_production_scenario():
    """Test the exact scenario happening in production"""
    print("🐛 DEBUGGING STATUS ERROR")
    print("=" * 50)
    
    # Exact parameters from production logs
    client_id = "77f276b5-5a0a-4888-be96-5ab3fa96b1b3"
    user_phone = "5561936180578@s.whatsapp.net"
    message_text = "Test message from production scenario"
    direction = "inbound"
    user_name = "Debug User"
    
    print(f"📝 Tentando salvar mensagem:")
    print(f"  - Client ID: {client_id}")
    print(f"  - User Phone: {user_phone}")
    print(f"  - Message: {message_text}")
    print(f"  - Direction: {direction}")
    print(f"  - User Name: {user_name}")
    
    try:
        result = save_message_to_database(client_id, user_phone, message_text, direction, user_name)
        print(f"✅ Resultado: {result}")
        return True
    except Exception as e:
        print(f"❌ Erro encontrado: {e}")
        print(f"❌ Tipo do erro: {type(e).__name__}")
        if hasattr(e, '__dict__'):
            print(f"❌ Detalhes: {e.__dict__}")
        return False

def test_all_status_values():
    """Test all possible status values to see which one is causing issues"""
    print("\n🧪 TESTANDO TODOS OS VALORES DE STATUS")
    print("=" * 50)
    
    client_id = "77f276b5-5a0a-4888-be96-5ab3fa96b1b3"
    user_phone = "5561936180578@s.whatsapp.net"
    
    # Valid status values according to enum
    valid_statuses = ['qualified', 'scheduled', 'none', 'lost', 'archived']
    
    # Test if there's any hidden status being used
    for status in valid_statuses:
        print(f"\n📝 Testando status: '{status}'")
        
        # Manually test by creating message_data structure
        from api.index import get_supabase_client
        supabase = get_supabase_client()
        
        if supabase:
            message_data = {
                "client_id": client_id,
                "user_id": user_phone,
                "user_name": "Test User",
                "message_direction": "inbound",
                "content": f"Test message with status {status}",
                "message_metadata": {},
                "status": status,  # Test each status
                "lead_score": 0
            }
            
            try:
                result = supabase.table('messages').insert(message_data).execute()
                if result.data:
                    print(f"  ✅ Status '{status}' funcionou!")
                else:
                    print(f"  ❌ Status '{status}' falhou - sem dados retornados")
            except Exception as e:
                print(f"  ❌ Status '{status}' falhou: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO DEBUG DO ERRO DE STATUS")
    print("=" * 60)
    
    # Test 1: Exact production scenario
    production_result = test_exact_production_scenario()
    
    # Test 2: All status values
    test_all_status_values()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DO DEBUG")
    print("=" * 60)
    print(f"Cenário de produção: {'✅ OK' if production_result else '❌ FALHA'}")
    print("\nSe o cenário de produção falhou, o problema está na nossa função.")
    print("Se passou, o problema pode estar em outro lugar do código em produção.")