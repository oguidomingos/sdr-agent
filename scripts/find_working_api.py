#!/usr/bin/env python3
"""
Script para encontrar a API que está funcionando
"""
import requests
import json

def test_api_urls():
    """Testa várias URLs da API"""
    print("🔍 Procurando API funcionando...")
    print("=" * 50)
    
    # URLs encontradas nos arquivos
    api_urls = [
        "https://sdr-agent-supabase.vercel.app/api",
        "https://sdr-agent-cc2d4bm0x-oguidomingos-projects.vercel.app/api",
        "https://sdr-agent-fzxylmlvo-oguidomingos-projects.vercel.app/api",
        "https://sdr-agent-hln7g9sdj-oguidomingos-projects.vercel.app/api",
        "https://sdr-agent-mdhjkliti-oguidomingos-projects.vercel.app/api",
        "https://sdr-agent-five.vercel.app/api",
    ]
    
    working_apis = []
    
    for api_url in api_urls:
        print(f"\n🌐 Testando: {api_url}")
        
        try:
            # Test health endpoint first
            health_response = requests.get(f"{api_url}/health", timeout=10)
            print(f"Health Status: {health_response.status_code}")
            
            if health_response.status_code == 200:
                print("✅ Health endpoint funcionando!")
                
                # Test auth login
                login_data = {
                    "email": "oguigodomingos@gmail.com",
                    "password": "180121430"
                }
                
                auth_response = requests.post(f"{api_url}/auth/login", json=login_data, timeout=10)
                print(f"Auth Status: {auth_response.status_code}")
                
                if auth_response.status_code == 200:
                    token_data = auth_response.json()
                    print("✅ Autenticação funcionando!")
                    
                    # Test /auth/me
                    headers = {
                        "Authorization": f"Bearer {token_data['access_token']}",
                        "Content-Type": "application/json"
                    }
                    
                    me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=10)
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        print(f"✅ Usuário: {user_data.get('first_name')} {user_data.get('last_name')}")
                        print(f"✅ Email: {user_data.get('email')}")
                        working_apis.append({
                            'url': api_url,
                            'user': user_data
                        })
                    else:
                        print(f"❌ /auth/me falhou: {me_response.status_code}")
                elif auth_response.status_code == 401:
                    print("❌ Credenciais inválidas")
                else:
                    print(f"❌ Auth falhou: {auth_response.status_code}")
            else:
                print(f"❌ Health falhou: {health_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Conexão recusada")
        except requests.exceptions.Timeout:
            print("❌ Timeout")
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    return working_apis

def main():
    """Função principal"""
    print("🚀 Localizador de API - SDR Agent")
    print("=" * 60)
    
    working_apis = test_api_urls()
    
    if working_apis:
        print(f"\n🎉 Encontradas {len(working_apis)} APIs funcionando:")
        print("=" * 50)
        
        for i, api in enumerate(working_apis, 1):
            print(f"\n{i}. {api['url']}")
            print(f"   Usuário: {api['user'].get('first_name')} {api['user'].get('last_name')}")
            print(f"   Email: {api['user'].get('email')}")
        
        # Recommend the first working API
        recommended_api = working_apis[0]['url']
        print(f"\n💡 RECOMENDAÇÃO:")
        print(f"Use esta API: {recommended_api}")
        
        # Extract base URL for frontend
        base_url = recommended_api.replace('/api', '')
        print(f"URL do frontend: {base_url}")
        
        print(f"\n🔧 CONFIGURAÇÃO:")
        print(f"1. Configure VITE_API_URL={recommended_api}")
        print(f"2. Acesse o frontend em: {base_url}")
        print(f"3. Faça login com: oguigodomingos@gmail.com / 180121430")
        
    else:
        print("\n❌ Nenhuma API funcionando encontrada")
        print("\n💡 POSSÍVEIS SOLUÇÕES:")
        print("1. Fazer um novo deploy na Vercel")
        print("2. Verificar logs da Vercel")
        print("3. Verificar configurações de ambiente")

if __name__ == "__main__":
    main()