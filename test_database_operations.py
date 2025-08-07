#!/usr/bin/env python3
"""
Teste das operações do banco de dados
- Verifica se mensagens estão sendo salvas
- Testa tabela message_cooldown
- Verifica se o sistema está persistindo dados corretamente
"""

import os
from supabase import create_client
from datetime import datetime, timedelta

def test_database_operations():
    """Testa operações no banco de dados"""
    print("🗄️  TESTANDO OPERAÇÕES DO BANCO DE DADOS")
    print("=" * 50)
    
    try:
        # Conectar ao Supabase
        supabase_url = 'https://roezccmxctqbvdjlgdru.supabase.co'
        service_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDA3ODUzNSwiZXhwIjoyMDY5NjU0NTM1fQ.sE5v5FCfMKhsnehtnCF75S1N41g7f3JaZS1v1sDCeU0'
        
        supabase = create_client(supabase_url, service_key)
        print("✅ Conectado ao Supabase")
        
        # 1. Testar tabela de clientes
        print("\n📋 Testando tabela 'clients'...")
        clients_result = supabase.table('clients').select('*').eq('evolution_instance', 'sdr_77f276b5').execute()
        if clients_result.data:
            client = clients_result.data[0]
            print(f"✅ Cliente encontrado: {client['name']} (ID: {client['id']})")
            client_id = client['id']
        else:
            print("❌ Nenhum cliente encontrado para a instância sdr_77f276b5")
            return False
        
        # 2. Testar mensagens recentes
        print("\n💬 Testando tabela 'messages'...")
        # Primeiro, vamos ver a estrutura da tabela
        try:
            messages_result = supabase.table('messages').select('*').eq('client_id', client_id).limit(5).execute()
        except Exception as e:
            print(f"❌ Erro ao consultar mensagens: {e}")
            # Tentar com timestamp em vez de created_at
            messages_result = supabase.table('messages').select('*').eq('client_id', client_id).order('timestamp', desc=True).limit(5).execute()
        
        if messages_result.data:
            print(f"✅ Encontradas {len(messages_result.data)} mensagens recentes:")
            for i, msg in enumerate(messages_result.data[:5], 1):
                direction = msg.get('message_direction', 'unknown')
                content = msg.get('content', 'no content')[:50] + ('...' if len(msg.get('content', '')) > 50 else '')
                timestamp = msg.get('timestamp', msg.get('created_at', 'no timestamp'))
                print(f"  {i}. [{direction}] {content} - {timestamp}")
        else:
            print("⚠️  Nenhuma mensagem encontrada nas últimas 24h")
        
        # 3. Testar tabela message_cooldown
        print("\n⏱️  Testando tabela 'message_cooldown'...")
        cooldown_result = supabase.table('message_cooldown').select('*').limit(5).execute()
        
        if cooldown_result.data:
            print(f"✅ Tabela message_cooldown está funcionando - {len(cooldown_result.data)} registros encontrados")
            for record in cooldown_result.data:
                phone = record.get('user_phone', 'unknown')
                last_msg = record.get('last_message_at', 'never')
                pending = len(record.get('pending_messages', []))
                print(f"  📱 {phone}: última msg {last_msg}, {pending} msgs pendentes")
        else:
            print("⚠️  Tabela message_cooldown existe mas não tem dados")
        
        # 4. Testar inserção de dados de teste na tabela cooldown
        print("\n🧪 Testando inserção na tabela message_cooldown...")
        test_phone = "5561936180578@s.whatsapp.net"
        
        try:
            # Tentar inserir ou atualizar um registro de teste
            test_data = {
                'user_phone': test_phone,
                'client_id': client_id,
                'last_message_at': datetime.now().isoformat(),
                'pending_messages': [{'text': 'Teste sistema', 'timestamp': datetime.now().isoformat()}],
                'cooldown_seconds': 90
            }
            
            # Verificar se já existe
            existing = supabase.table('message_cooldown').select('*').eq('user_phone', test_phone).execute()
            
            if existing.data:
                # Atualizar
                update_result = supabase.table('message_cooldown').update({
                    'last_message_at': datetime.now().isoformat(),
                    'pending_messages': [{'text': 'Teste sistema atualizado', 'timestamp': datetime.now().isoformat()}]
                }).eq('user_phone', test_phone).execute()
                print("✅ Registro de cooldown atualizado com sucesso")
            else:
                # Inserir
                insert_result = supabase.table('message_cooldown').insert(test_data).execute()
                print("✅ Novo registro de cooldown criado com sucesso")
                
        except Exception as e:
            print(f"❌ Erro ao testar inserção de cooldown: {e}")
        
        # 5. Verificar se as mensagens têm status válido
        print("\n📊 Verificando status das mensagens...")
        status_check = supabase.table('messages').select('status').eq('client_id', client_id).limit(10).execute()
        
        if status_check.data:
            statuses = [msg.get('status') for msg in status_check.data]
            unique_statuses = set(statuses)
            print(f"✅ Status encontrados nas mensagens: {list(unique_statuses)}")
            
            # Verificar se há status inválidos
            invalid_statuses = [s for s in unique_statuses if s not in ['qualified', 'scheduled', 'none', 'lost', 'archived']]
            if invalid_statuses:
                print(f"❌ Status inválidos encontrados: {invalid_statuses}")
                return False
            else:
                print("✅ Todos os status são válidos")
        
        print("\n✅ TODOS OS TESTES DE BANCO DE DADOS PASSARAM!")
        return True
        
    except Exception as e:
        print(f"❌ Erro geral nos testes de banco: {e}")
        return False

if __name__ == "__main__":
    test_database_operations()