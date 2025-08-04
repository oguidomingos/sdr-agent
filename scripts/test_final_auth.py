#!/usr/bin/env python3
"""
Script final para testar autenticação
"""
import requests
import json

def test_final_auth():
    """Teste final da autenticação"""
    api_url = "https://sdr-agent-five.vercel.app/api"
    
    print("🔐 Teste Final de Autenticação")
    print("=" * 50)
    print(f"🌐 API: {api_url}")
    
    # Test login with real user
    print("\n1️⃣ Fazendo login com usuário real...")
    login_data = {
        "email": "oguigodomingos@gmail.com",
        "password": "180121430"
    }
    
    try:
        response = requests.post(f"{api_url}/auth/login", json=login_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login bem-sucedido!")
            print(f"Token: {token_data.get('access_token', 'N/A')[:50]}...")
            print(f"User ID: {token_data.get('user_id', 'N/A')}")
            print(f"Email: {token_data.get('email', 'N/A')}")
            
            # Test /auth/me
            print("\n2️⃣ Obtendo dados do usuário...")
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "Content-Type": "application/json"
            }
            
            me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=10)
            print(f"Status: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print("✅ Dados do usuário obtidos!")
                print(f"ID: {user_data.get('id', 'N/A')}")
                print(f"Email: {user_data.get('email', 'N/A')}")
                print(f"Nome: {user_data.get('first_name', 'N/A')} {user_data.get('last_name', 'N/A')}")
                print(f"Status: {user_data.get('status', 'N/A')}")
                print(f"Plano: {user_data.get('plan', 'N/A')}")
                
                # Check if data is correct
                if user_data.get('email') == 'oguigodomingos@gmail.com':
                    print("\n🎉 PERFEITO! Dados corretos retornados!")
                    
                    # Test clients
                    print("\n3️⃣ Obtendo lista de clientes...")
                    clients_response = requests.get(f"{api_url}/clients/", headers=headers, timeout=10)
                    print(f"Status: {clients_response.status_code}")
                    
                    if clients_response.status_code == 200:
                        clients_data = clients_response.json()
                        print(f"✅ Total de clientes: {clients_data.get('total', 0)}")
                        
                        for client in clients_data.get('items', []):
                            print(f"  - {client.get('name', 'N/A')} ({client.get('domain', 'N/A')})")
                    else:
                        print(f"❌ Erro ao obter clientes: {clients_response.text}")
                    
                    return True
                else:
                    print(f"❌ Dados incorretos! Email retornado: {user_data.get('email')}")
                    print("A API ainda está retornando dados mockados")
            else:
                print(f"❌ Erro ao obter dados do usuário: {me_response.text}")
        else:
            print(f"❌ Erro no login: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    return False

def main():
    """Função principal"""
    print("🚀 Teste Final de Autenticação - SDR Agent")
    print("=" * 60)
    
    if test_final_auth():
        print("\n🎯 SOLUÇÃO FINAL:")
        print("=" * 30)
        print("✅ A API está funcionando corretamente!")
        print("✅ Seu usuário real existe e funciona!")
        print("✅ Os dados estão sendo retornados corretamente!")
        print("\n🌐 ACESSE:")
        print("URL: https://sdr-agent-five.vercel.app")
        print("Email: oguigodomingos@gmail.com")
        print("Senha: 180121430")
        print("\n💡 IMPORTANTE:")
        print("1. Limpe o localStorage do navegador")
        print("2. Faça logout se estiver logado")
        print("3. Faça login com as credenciais acima")
        print("4. Agora você deve ver 'Guigo Domingos' ao invés de 'Demo User'")
    else:
        print("\n❌ Ainda há problemas na API")
        print("A API pode estar retornando dados mockados")

if __name__ == "__main__":
    main()