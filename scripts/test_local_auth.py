#!/usr/bin/env python3
"""
Script para testar a API de autenticação local
"""
import requests
import json

def test_local_auth():
    """Testa a API de autenticação local"""
    print("🔐 Testando API de Autenticação Local")
    print("=" * 50)
    
    # Test different API URLs
    api_urls = [
        "http://localhost:3000/api",  # Frontend dev server proxy
        "http://localhost:8000/api",  # Direct backend
        "https://sdr-agent-supabase.vercel.app/api",  # Production
    ]
    
    login_data = {
        "email": "oguigodomingos@gmail.com",
        "password": "180121430"
    }
    
    for api_url in api_urls:
        print(f"\n🌐 Testando: {api_url}")
        
        try:
            response = requests.post(f"{api_url}/auth/login", json=login_data, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                print("✅ Login bem-sucedido!")
                print(f"User ID: {token_data.get('user_id', 'N/A')}")
                print(f"Email: {token_data.get('email', 'N/A')}")
                
                # Test /auth/me endpoint
                headers = {
                    "Authorization": f"Bearer {token_data['access_token']}",
                    "Content-Type": "application/json"
                }
                
                me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=10)
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print(f"Nome: {user_data.get('first_name', 'N/A')} {user_data.get('last_name', 'N/A')}")
                    print(f"Email: {user_data.get('email', 'N/A')}")
                    print("🎉 API funcionando corretamente!")
                    return api_url  # Return working API URL
                else:
                    print(f"❌ Erro no /auth/me: {me_response.status_code}")
                    
            elif response.status_code == 404:
                print("❌ API não encontrada (404)")
            elif response.status_code == 401:
                print("❌ Credenciais inválidas (401)")
            else:
                print(f"❌ Erro: {response.status_code} - {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Conexão recusada - API não está rodando")
        except requests.exceptions.Timeout:
            print("❌ Timeout - API não respondeu")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return None

def check_frontend_config():
    """Verifica a configuração do frontend"""
    print("\n📱 Verificando configuração do frontend...")
    
    # Check if frontend is running
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend rodando em http://localhost:3000")
        else:
            print(f"⚠️  Frontend respondeu com status {response.status_code}")
    except:
        print("❌ Frontend não está rodando em http://localhost:3000")
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend rodando em http://localhost:8000")
        else:
            print(f"⚠️  Backend respondeu com status {response.status_code}")
    except:
        print("❌ Backend não está rodando em http://localhost:8000")

def main():
    """Função principal"""
    print("🚀 Teste de Autenticação Local - SDR Agent")
    print("=" * 60)
    
    working_api = test_local_auth()
    check_frontend_config()
    
    if working_api:
        print(f"\n🎯 API funcionando em: {working_api}")
        print("\n💡 SOLUÇÃO:")
        print("1. Certifique-se de que o frontend está configurado para usar esta API")
        print("2. Verifique se a variável VITE_API_URL está correta")
        print("3. Limpe o cache do navegador e localStorage")
        print("4. Faça login novamente")
    else:
        print("\n❌ Nenhuma API está funcionando")
        print("\n💡 POSSÍVEIS SOLUÇÕES:")
        print("1. Inicie o backend local: python -m uvicorn api.main:app --reload --port 8000")
        print("2. Inicie o frontend: npm run dev")
        print("3. Verifique as configurações de CORS")
        print("4. Verifique as variáveis de ambiente")

if __name__ == "__main__":
    main()