#!/usr/bin/env python3
"""
Script para criar um usuário real no sistema
"""
import os
import sys
import bcrypt
import uuid

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
    
    def create_user():
        """Cria um usuário real"""
        print("👤 Criando usuário real no sistema")
        print("=" * 40)
        
        # Get user input
        email = input("📧 Digite seu email: ").strip()
        if not email or '@' not in email:
            print("❌ Email inválido")
            return
        
        first_name = input("👤 Digite seu primeiro nome: ").strip()
        if not first_name:
            print("❌ Nome é obrigatório")
            return
        
        last_name = input("👤 Digite seu sobrenome (opcional): ").strip() or None
        
        password = input("🔑 Digite uma senha (mínimo 6 caracteres): ").strip()
        if len(password) < 6:
            print("❌ Senha deve ter pelo menos 6 caracteres")
            return
        
        # Get Supabase credentials
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            print("❌ Variáveis de ambiente do Supabase não encontradas")
            return
        
        try:
            client = create_client(url, key)
            
            # Check if user already exists
            result = client.table('users').select('*').eq('email', email).execute()
            if result.data:
                print(f"❌ Usuário com email {email} já existe")
                return
            
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user data
            user_data = {
                "id": str(uuid.uuid4()),
                "email": email,
                "hashed_password": hashed_password,
                "first_name": first_name,
                "last_name": last_name,
                "status": "active",
                "plan": "free"
            }
            
            # Insert user
            result = client.table('users').insert(user_data).execute()
            
            if result.data:
                user = result.data[0]
                print("\n✅ Usuário criado com sucesso!")
                print("-" * 40)
                print(f"📧 Email: {user['email']}")
                print(f"👤 Nome: {user['first_name']} {user.get('last_name', '')}")
                print(f"🆔 ID: {user['id']}")
                print(f"🔑 Senha: {password}")
                
                print("\n🎉 PRÓXIMOS PASSOS:")
                print("1. Faça logout no frontend")
                print("2. Limpe o localStorage do navegador (F12 > Application > Local Storage > Clear)")
                print("3. Faça login com as credenciais acima")
                print("4. Agora você verá seu nome real ao invés de 'Demo User'")
                
            else:
                print("❌ Erro ao criar usuário")
                
        except Exception as e:
            print(f"❌ Erro ao conectar com Supabase: {e}")
            
    def main():
        """Função principal"""
        print("🚀 Criador de Usuário Real - SDR Agent")
        print("=" * 50)
        
        create_user()
        
except ImportError:
    print("❌ Biblioteca 'supabase' não encontrada")
    print("Execute: pip3 install supabase --break-system-packages")

if __name__ == "__main__":
    main()