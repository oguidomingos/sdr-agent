#!/usr/bin/env python3
"""
Script para testar a API funcionando
"""
import requests
import json

def test_working_api():
    """Testa a API que está funcionando"""
    api_url = "https://sdr-agent-five.vercel.app/api"
    
    print("🔐 Testando API Funcionando")
    print("=" * 50)
    print(f"🌐 API: {api_url}")
    
    # Test 1: Login with demo user
    print("\n1️⃣ Testando login com usuário demo...")
    demo_login = {
        "email": "demo@sdr-agent.com",
        "password": "demo123"
    }
    
    try:
        response = requests.post(f"{api_url}/auth/login", json=demo_login, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Usuário demo existe e funciona")
            token_data = response.json()
            
            # Get demo user info
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "Content-Type": "application/json"
            }
            
            me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=10)
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"Demo user: {user_data.get('first_name')} {user_data.get('last_name')}")
                print(f"Demo email: {user_data.get('email')}")
        else:
            print("❌ Usuário demo não funciona")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Test 2: Login with real user
    print("\n2️⃣ Testando login com usuário real...")
    real_login = {
        "email": "oguigodomingos@gmail.com",
        "password": "180121430"
    }
    
    try:
        response = requests.post(f"{api_url}/auth/login", json=real_login, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Usuário real existe e funciona!")
            token_data = response.json()
            
            # Get real user info
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "Content-Type": "application/json"
            }
            
            me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=10)
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ Usuário real: {user_data.get('first_name')} {user_data.get('last_name')}")
                print(f"✅ Email real: {user_data.get('email')}")
                
                # Test clients endpoint
                print("\n3️⃣ Testando endpoint de clientes...")
                clients_response = requests.get(f"{api_url}/clients/", headers=headers, timeout=10)
                print(f"Clients Status: {clients_response.status_code}")
                
                if clients_response.status_code == 200:
                    clients_data = clients_response.json()
                    print(f"✅ Total de clientes: {clients_data.get('total', 0)}")
                    
                    for client in clients_data.get('items', []):
                        print(f"  - {client.get('name', 'N/A')} ({client.get('domain', 'N/A')})")
                else:
                    print(f"❌ Erro ao obter clientes: {clients_response.text}")
                
                return True
            else:
                print(f"❌ Erro ao obter dados do usuário real: {me_response.text}")
        elif response.status_code == 401:
            print("❌ Usuário real não existe ou credenciais inválidas")
        else:
            print(f"❌ Erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return False

def main():
    """Função principal"""
    print("🚀 Teste da API Funcionando - SDR Agent")
    print("=" * 60)
    
    if test_working_api():
        print("\n🎉 SOLUÇÃO ENCONTRADA!")
        print("=" * 30)
        print("1. A API está funcionando em: https://sdr-agent-five.vercel.app/api")
        print("2. Seu usuário real existe e funciona")
        print("3. Acesse: https://sdr-agent-five.vercel.app")
        print("4. Faça login com: oguigodomingos@gmail.com / 180121430")
        print("5. Agora você deve ver seus dados reais!")
    else:
        print("\n❌ Usuário real não encontrado nesta API")
        print("Você precisa criar o usuário real nesta API ou usar outra API")

if __name__ == "__main__":
    main()