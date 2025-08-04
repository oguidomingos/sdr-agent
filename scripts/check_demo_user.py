#!/usr/bin/env python3
"""
Script simples para verificar e remover usuário demo
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from supabase import create_client, Client

def get_supabase_client():
    """Get Supabase client"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Variáveis de ambiente do Supabase não encontradas")
        print("Certifique-se de que SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY estão definidas")
        return None
    
    return create_client(url, key)

def check_users():
    """Verifica usuários no sistema"""
    client = get_supabase_client()
    if not client:
        return
    
    print("🔍 Verificando usuários no sistema...")
    
    try:
        # Get all users
        result = client.table('users').select('*').execute()
        users = result.data
        
        if not users:
            print("❌ Nenhum usuário encontrado no sistema")
            return
        
        print(f"\n📊 Encontrados {len(users)} usuários:")
        print("-" * 80)
        
        demo_user = None
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Email: {user['email']}")
            print(f"Nome: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
            print(f"Status: {user['status']}")
            print(f"Criado em: {user['created_at']}")
            
            if user['email'] == 'demo@sdr-agent.com':
                print("⚠️  USUÁRIO DEMO DETECTADO")
                demo_user = user
            
            print("-" * 80)
        
        if demo_user:
            print("\n🚨 PROBLEMA IDENTIFICADO:")
            print("Existe um usuário demo no sistema que está causando confusão.")
            print("Este é o usuário que aparece como 'Demo User' no frontend.")
            
            response = input("\n❓ Deseja remover os dados demo? (s/n): ").lower().strip()
            if response == 's':
                remove_demo_data(client, demo_user['id'])
        else:
            print("\n✅ Nenhum usuário demo encontrado.")
            
    except Exception as e:
        print(f"❌ Erro ao verificar usuários: {e}")

def remove_demo_data(client, demo_user_id):
    """Remove dados demo do sistema"""
    print("\n🧹 Removendo dados demo...")
    
    try:
        # Remove in order (due to foreign key constraints)
        
        # 1. Remove demo messages
        result = client.table('messages').delete().eq('client_id', '660e8400-e29b-41d4-a716-446655440000').execute()
        print(f"✅ Removidas mensagens demo")
        
        # 2. Remove demo agent configs
        result = client.table('agent_configs').delete().eq('client_id', '660e8400-e29b-41d4-a716-446655440000').execute()
        print(f"✅ Removidas configurações de agente demo")
        
        # 3. Remove demo playbooks
        result = client.table('playbooks').delete().eq('client_id', '660e8400-e29b-41d4-a716-446655440000').execute()
        print(f"✅ Removidos playbooks demo")
        
        # 4. Remove demo client
        result = client.table('clients').delete().eq('id', '660e8400-e29b-41d4-a716-446655440000').execute()
        print(f"✅ Removido cliente demo")
        
        # 5. Remove demo user
        result = client.table('users').delete().eq('id', demo_user_id).execute()
        print(f"✅ Removido usuário demo")
        
        print("\n🎉 Dados demo removidos com sucesso!")
        print("💡 Agora você precisa:")
        print("1. Fazer logout no frontend (limpar localStorage)")
        print("2. Criar uma nova conta ou fazer login com sua conta real")
        
    except Exception as e:
        print(f"❌ Erro ao remover dados demo: {e}")

def main():
    """Função principal"""
    print("🚀 Verificador de Usuários Demo - SDR Agent")
    print("=" * 50)
    
    check_users()

if __name__ == "__main__":
    main()