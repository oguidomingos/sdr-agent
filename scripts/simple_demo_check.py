#!/usr/bin/env python3
"""
Script simples para verificar usuário demo sem dependências extras
"""
import os
import sys
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

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

try:
    from supabase import create_client
    
    def main():
        """Função principal"""
        print("🚀 Verificador de Usuários Demo - SDR Agent")
        print("=" * 50)
        
        # Get Supabase credentials
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            print("❌ Variáveis de ambiente do Supabase não encontradas")
            print("Verifique se SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY estão no arquivo .env")
            return
        
        print(f"🔗 Conectando ao Supabase: {url[:30]}...")
        
        try:
            client = create_client(url, key)
            
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
                print(f"Email: {user['email']}")
                print(f"Nome: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
                print(f"Status: {user['status']}")
                
                if user['email'] == 'demo@sdr-agent.com':
                    print("⚠️  USUÁRIO DEMO DETECTADO - Este é o problema!")
                    demo_user = user
                
                print("-" * 40)
            
            if demo_user:
                print("\n🚨 SOLUÇÃO:")
                print("1. Faça logout no frontend")
                print("2. Limpe o localStorage do navegador (F12 > Application > Local Storage > Clear)")
                print("3. Crie uma nova conta com seu email real")
                print("4. Ou use as credenciais de um usuário real se já existir")
                
                print(f"\n📧 Usuários disponíveis (exceto demo):")
                real_users = [u for u in users if u['email'] != 'demo@sdr-agent.com']
                for user in real_users:
                    print(f"- {user['email']} ({user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')})")
                
                if not real_users:
                    print("- Nenhum usuário real encontrado. Você precisa criar uma conta nova.")
            else:
                print("\n✅ Nenhum usuário demo encontrado. O problema pode ser outro.")
                
        except Exception as e:
            print(f"❌ Erro ao conectar com Supabase: {e}")
            
except ImportError:
    print("❌ Biblioteca 'supabase' não encontrada")
    print("Execute: pip3 install supabase --break-system-packages")
    print("Ou use um ambiente virtual")

if __name__ == "__main__":
    main()