#!/usr/bin/env python3
"""
Script para verificar qual usuário está logado e limpar dados demo se necessário
"""
import asyncio
import os
import sys
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.supabase_db import get_supabase_db

async def check_current_users():
    """Verifica todos os usuários no sistema"""
    db = get_supabase_db()
    
    print("🔍 Verificando usuários no sistema...")
    
    try:
        # Get all users
        result = db.client.table('users').select('*').execute()
        users = result.data
        
        if not users:
            print("❌ Nenhum usuário encontrado no sistema")
            return
        
        print(f"\n📊 Encontrados {len(users)} usuários:")
        print("-" * 80)
        
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Email: {user['email']}")
            print(f"Nome: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
            print(f"Status: {user['status']}")
            print(f"Plano: {user['plan']}")
            print(f"Criado em: {user['created_at']}")
            print(f"Último login: {user.get('last_login', 'Nunca')}")
            
            # Check if this is demo user
            if user['email'] == 'demo@sdr-agent.com':
                print("⚠️  USUÁRIO DEMO DETECTADO")
            
            print("-" * 80)
        
        # Check for demo data
        demo_user = next((u for u in users if u['email'] == 'demo@sdr-agent.com'), None)
        if demo_user:
            print("\n🚨 PROBLEMA IDENTIFICADO:")
            print("Existe um usuário demo no sistema que pode estar causando confusão.")
            print("Este usuário tem os dados:")
            print(f"- Nome: {demo_user.get('first_name')} {demo_user.get('last_name')}")
            print(f"- Email: {demo_user['email']}")
            
            # Ask if user wants to remove demo data
            response = input("\n❓ Deseja remover os dados demo? (s/n): ").lower().strip()
            if response == 's':
                await remove_demo_data(db, demo_user['id'])
        
    except Exception as e:
        print(f"❌ Erro ao verificar usuários: {e}")

async def remove_demo_data(db, demo_user_id):
    """Remove dados demo do sistema"""
    print("\n🧹 Removendo dados demo...")
    
    try:
        # Remove demo messages
        result = db.client.table('messages').delete().eq('client_id', '660e8400-e29b-41d4-a716-446655440000').execute()
        print(f"✅ Removidas {len(result.data) if result.data else 0} mensagens demo")
        
        # Remove demo agent configs
        result = db.client.table('agent_configs').delete().eq('client_id', '660e8400-e29b-41d4-a716-446655440000').execute()
        print(f"✅ Removidas {len(result.data) if result.data else 0} configurações de agente demo")
        
        # Remove demo playbooks
        result = db.client.table('playbooks').delete().eq('client_id', '660e8400-e29b-41d4-a716-446655440000').execute()
        print(f"✅ Removidos {len(result.data) if result.data else 0} playbooks demo")
        
        # Remove demo client
        result = db.client.table('clients').delete().eq('id', '660e8400-e29b-41d4-a716-446655440000').execute()
        print(f"✅ Removido {len(result.data) if result.data else 0} cliente demo")
        
        # Remove demo user
        result = db.client.table('users').delete().eq('id', demo_user_id).execute()
        print(f"✅ Removido {len(result.data) if result.data else 0} usuário demo")
        
        print("\n🎉 Dados demo removidos com sucesso!")
        print("💡 Agora você pode fazer login com sua conta real ou criar uma nova conta.")
        
    except Exception as e:
        print(f"❌ Erro ao remover dados demo: {e}")

async def create_real_user():
    """Cria um usuário real para teste"""
    db = get_supabase_db()
    
    print("\n👤 Criando usuário real para teste...")
    
    email = input("Digite seu email: ").strip()
    first_name = input("Digite seu primeiro nome: ").strip()
    last_name = input("Digite seu sobrenome (opcional): ").strip() or None
    
    # Simple password hash for demo (in production, use proper bcrypt)
    import bcrypt
    password = "123456"  # Default password for testing
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        user_data = {
            "email": email,
            "hashed_password": hashed_password,
            "first_name": first_name,
            "last_name": last_name,
            "status": "active",
            "plan": "free"
        }
        
        result = db.client.table('users').insert(user_data).execute()
        
        if result.data:
            user = result.data[0]
            print(f"✅ Usuário criado com sucesso!")
            print(f"📧 Email: {user['email']}")
            print(f"👤 Nome: {user['first_name']} {user.get('last_name', '')}")
            print(f"🔑 Senha padrão: {password}")
            print("\n💡 Você pode fazer login com essas credenciais no frontend.")
        else:
            print("❌ Erro ao criar usuário")
            
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")

async def main():
    """Função principal"""
    print("🚀 Verificador de Usuários - SDR Agent")
    print("=" * 50)
    
    await check_current_users()
    
    # Ask if user wants to create a real user
    response = input("\n❓ Deseja criar um usuário real para teste? (s/n): ").lower().strip()
    if response == 's':
        await create_real_user()

if __name__ == "__main__":
    asyncio.run(main())