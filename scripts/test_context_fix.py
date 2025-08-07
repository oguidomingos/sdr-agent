#!/usr/bin/env python3
"""
Script para testar as correções de contexto e prompt
"""

import os
import sys
sys.path.append('/Users/oguidomingos/sdr-agent')

# Import da API principal
from api.index import (
    get_conversation_history, 
    process_with_gemini_ai,
    save_message_to_database,
    get_client_by_instance,
    get_supabase_client
)

def test_context_fix():
    """Teste as correções de contexto"""
    
    print("=" * 60)
    print("TESTE DAS CORREÇÕES DE CONTEXTO E PROMPT")
    print("=" * 60)
    
    # 1. Testar conexão com Supabase
    print("\n1. TESTANDO CONEXÃO COM SUPABASE...")
    supabase = get_supabase_client()
    if supabase:
        print("✅ Conexão com Supabase estabelecida")
    else:
        print("❌ Falha na conexão com Supabase")
        print("Verifique as variáveis SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY")
        return
    
    # 2. Buscar cliente específico sdr_77f276b5
    print("\n2. BUSCANDO CLIENTE sdr_77f276b5...")
    client_config = get_client_by_instance("sdr_77f276b5")
    
    if client_config:
        print(f"✅ Cliente encontrado: {client_config.get('name', 'N/A')}")
        print(f"   - ID: {client_config.get('id', 'N/A')}")
        print(f"   - Agent Name: {client_config.get('agent_name', 'N/A')}")
        print(f"   - Agent Persona (prompt): {len(client_config.get('agent_persona', ''))} caracteres")
        if client_config.get('agent_persona'):
            print(f"   - Preview do prompt: {client_config.get('agent_persona', '')[:100]}...")
    else:
        print("❌ Cliente não encontrado")
        print("Listando clientes disponíveis...")
        try:
            result = supabase.table('clients').select('name, evolution_instance').execute()
            for client in result.data[:5]:
                print(f"   - {client.get('name', 'N/A')} ({client.get('evolution_instance', 'N/A')})")
        except Exception as e:
            print(f"Erro ao listar clientes: {e}")
        return
    
    # 3. Testar histórico de conversas
    print("\n3. TESTANDO HISTÓRICO DE CONVERSAS...")
    user_phone = "5561936180578@s.whatsapp.net"  # Número do exemplo
    client_id = client_config.get('id')
    
    # Primeiro, salvar algumas mensagens de teste
    print("   Salvando mensagens de teste...")
    save_message_to_database(client_id, user_phone, "opa", "inbound", "Guigo")
    save_message_to_database(client_id, user_phone, "Opa! Tudo bem?", "outbound", "")
    save_message_to_database(client_id, user_phone, "preciso de mais leads", "inbound", "Guigo")
    
    # Buscar histórico
    history = get_conversation_history(user_phone, client_id, limit=5)
    print(f"   Histórico obtido: {len(history)} caracteres")
    if history:
        print("   Preview do histórico:")
        print("   " + history.replace('\n', '\n   '))
    else:
        print("   ❌ Nenhum histórico encontrado")
    
    # 4. Testar processamento com Gemini AI
    print("\n4. TESTANDO PROCESSAMENTO COM GEMINI AI...")
    try:
        # Simular uma mensagem que deveria ter contexto
        test_message = "não entendo direito o que vocês fazem, pode me explicar melhor?"
        
        response = process_with_gemini_ai(test_message, client_config, user_phone)
        
        if response:
            print(f"✅ Resposta gerada: {len(response)} caracteres")
            print(f"   Preview: {response[:200]}...")
        else:
            print("❌ Nenhuma resposta gerada")
            
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    test_context_fix()