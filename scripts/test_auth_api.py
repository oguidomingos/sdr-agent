#!/usr/bin/env python3
"""
Script para testar a API de autenticação
"""
import os
import sys
import requests
import json

def load_env_file():
    """Load environment variables from .env file"""
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")

# Load environment
load_env_file()

def test_auth_api():
    """Testa a API de autenticação"""
    print("🔐 Testando API de Autenticação")
    print("=" * 50)
    
    # Get API URL
    api_url = "https://sdr-agent-supabase.vercel.app/api"  # Production URL
    
    print(f"🌐 API URL: {api_url}")
    
    # Test 1: Login with real user
    print("\n1️⃣ Testando login com usuário real...")
    login_data = {
        "email": "oguigodomingos@gmail.com",
        "password": "180121430"
    }
    
    try:
        response = requests.post(f"{api_url}/auth/login", json=login_data, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login bem-sucedido!")
            print(f"Token: {token_data.get('access_token', 'N/A')[:50]}...")
            print(f"User ID: {token_data.get('user_id', 'N/A')}")
            print(f"Email: {token_data.get('email', 'N/A')}")
            
            # Test 2: Get user info with token
            print("\n2️⃣ Testando endpoint /auth/me...")
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "Content-Type": "application/json"
            }
            
            me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=30)
            print(f"Status: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print("✅ Dados do usuário obtidos com sucesso!")
                print(f"ID: {user_data.get('id', 'N/A')}")
                print(f"Email: {user_data.get('email', 'N/A')}")
                print(f"Nome: {user_data.get('first_name', 'N/A')} {user_data.get('last_name', 'N/A')}")
                print(f"Status: {user_data.get('status', 'N/A')}")
                print(f"Plano: {user_data.get('plan', 'N/A')}")
                
                # Test 3: Get clients for this user
                print("\n3️⃣ Testando endpoint /clients...")
                clients_response = requests.get(f"{api_url}/clients/", headers=headers, timeout=30)
                print(f"Status: {clients_response.status_code}")
                
                if clients_response.status_code == 200:
                    clients_data = clients_response.json()
                    print("✅ Lista de clientes obtida com sucesso!")
                    print(f"Total de clientes: {clients_data.get('total', 0)}")
                    print(f"Clientes: {len(clients_data.get('items', []))}")
                    
                    for client in clients_data.get('items', []):
                        print(f"  - {client.get('name', 'N/A')} ({client.get('domain', 'N/A')})")
                else:
                    print(f"❌ Erro ao obter clientes: {clients_response.text}")
                    
            else:
                print(f"❌ Erro ao obter dados do usuário: {me_response.text}")
                
        else:
            print(f"❌ Erro no login: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Test 4: Check if demo user still exists
    print("\n4️⃣ Verificando se usuário demo ainda existe...")
    demo_login_data = {
        "email": "demo@sdr-agent.com",
        "password": "demo123"
    }
    
    try:
        demo_response = requests.post(f"{api_url}/auth/login", json=demo_login_data, timeout=30)
        if demo_response.status_code == 200:
            print("⚠️  Usuário demo ainda existe no sistema!")
            demo_token = demo_response.json()
            
            # Get demo user info
            headers = {
                "Authorization": f"Bearer {demo_token['access_token']}",
                "Content-Type": "application/json"
            }
            
            demo_me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=30)
            if demo_me_response.status_code == 200:
                demo_user = demo_me_response.json()
                print(f"Demo user: {demo_user.get('first_name', 'N/A')} {demo_user.get('last_name', 'N/A')}")
                print(f"Demo email: {demo_user.get('email', 'N/A')}")
        else:
            print("✅ Usuário demo não existe ou foi removido")
            
    except Exception as e:
        print(f"❌ Erro ao testar usuário demo: {e}")

def main():
    """Função principal"""
    print("🚀 Teste de API de Autenticação - SDR Agent")
    print("=" * 60)
    
    test_auth_api()

if __name__ == "__main__":
    main()