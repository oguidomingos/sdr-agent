#!/usr/bin/env python3
"""
Script para criar usuário real na API que está funcionando
"""
import requests
import json

def create_user_in_api():
    """Cria usuário real na API funcionando"""
    api_url = "https://sdr-agent-five.vercel.app/api"
    
    print("👤 Criando usuário real na API funcionando")
    print("=" * 50)
    print(f"🌐 API: {api_url}")
    
    # Try to register new user
    print("\n1️⃣ Tentando registrar usuário real...")
    register_data = {
        "email": "oguigodomingos@gmail.com",
        "password": "180121430",
        "first_name": "Guigo",
        "last_name": "Domingos"
    }
    
    try:
        response = requests.post(f"{api_url}/auth/register", json=register_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Usuário criado com sucesso!")
            user_data = response.json()
            print(f"ID: {user_data.get('id', 'N/A')}")
            print(f"Email: {user_data.get('email', 'N/A')}")
            print(f"Nome: {user_data.get('first_name', 'N/A')} {user_data.get('last_name', 'N/A')}")
            
            # Now try to login
            print("\n2️⃣ Testando login com usuário criado...")
            login_data = {
                "email": "oguigodomingos@gmail.com",
                "password": "180121430"
            }
            
            login_response = requests.post(f"{api_url}/auth/login", json=login_data, timeout=10)
            print(f"Login Status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                print("✅ Login bem-sucedido!")
                
                # Test /auth/me
                headers = {
                    "Authorization": f"Bearer {token_data['access_token']}",
                    "Content-Type": "application/json"
                }
                
                me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=10)
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print(f"✅ Dados do usuário: {me_data.get('first_name')} {me_data.get('last_name')}")
                    print(f"✅ Email: {me_data.get('email')}")
                    
                    if me_data.get('email') == 'oguigodomingos@gmail.com':
                        print("\n🎉 SUCESSO! Usuário real funcionando corretamente!")
                        return True
                    else:
                        print(f"❌ API ainda retorna dados errados: {me_data.get('email')}")
                else:
                    print(f"❌ Erro no /auth/me: {me_response.text}")
            else:
                print(f"❌ Erro no login: {login_response.text}")
                
        elif response.status_code == 400:
            error_data = response.json()
            if "already registered" in error_data.get('detail', '').lower():
                print("⚠️  Usuário já existe, tentando login...")
                
                # Try login directly
                login_data = {
                    "email": "oguigodomingos@gmail.com",
                    "password": "180121430"
                }
                
                login_response = requests.post(f"{api_url}/auth/login", json=login_data, timeout=10)
                print(f"Login Status: {login_response.status_code}")
                
                if login_response.status_code == 200:
                    print("✅ Login funcionou! Problema pode estar no /auth/me")
                    return True
                else:
                    print(f"❌ Login falhou: {login_response.text}")
            else:
                print(f"❌ Erro no registro: {error_data.get('detail', 'Erro desconhecido')}")
        else:
            print(f"❌ Erro no registro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    return False

def test_api_endpoints():
    """Testa vários endpoints da API"""
    api_url = "https://sdr-agent-five.vercel.app/api"
    
    print("\n🔍 Testando endpoints da API...")
    
    endpoints = [
        "/health",
        "/auth/login",
        "/auth/register", 
        "/auth/me",
        "/clients/",
    ]
    
    for endpoint in endpoints:
        try:
            if endpoint in ["/auth/login", "/auth/register"]:
                # These need POST with data
                continue
                
            response = requests.get(f"{api_url}{endpoint}", timeout=5)
            print(f"{endpoint}: {response.status_code}")
            
        except Exception as e:
            print(f"{endpoint}: Erro - {e}")

def main():
    """Função principal"""
    print("🚀 Criador de Usuário na API Funcionando - SDR Agent")
    print("=" * 70)
    
    test_api_endpoints()
    
    if create_user_in_api():
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Acesse: https://sdr-agent-five.vercel.app")
        print("2. Faça login com: oguigodomingos@gmail.com / 180121430")
        print("3. Agora você deve ver seus dados reais!")
    else:
        print("\n❌ Não foi possível criar/verificar usuário real")
        print("Pode haver um problema na implementação da API")

if __name__ == "__main__":
    main()