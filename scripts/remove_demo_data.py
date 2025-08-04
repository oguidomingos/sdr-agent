#!/usr/bin/env python3
"""
Script para remover dados demo do sistema
"""
import os
import sys

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
    
    def remove_demo_data():
        """Remove dados demo do sistema"""
        print("🧹 Removendo dados demo do sistema")
        print("=" * 40)
        
        # Get Supabase credentials
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            print("❌ Variáveis de ambiente do Supabase não encontradas")
            return
        
        try:
            client = create_client(url, key)
            
            # Confirm action
            response = input("⚠️  Tem certeza que deseja remover TODOS os dados demo? (s/n): ").lower().strip()
            if response != 's':
                print("❌ Operação cancelada")
                return
            
            print("\n🗑️  Removendo dados demo...")
            
            # Remove in order (due to foreign key constraints)
            
            # 1. Remove demo messages
            try:
                result = client.table('messages').delete().eq('client_id', '660e8400-e29b-41d4-a716-446655440000').execute()
                print("✅ Mensagens demo removidas")
            except Exception as e:
                print(f"⚠️  Erro ao remover mensagens: {e}")
            
            # 2. Remove demo agent configs
            try:
                result = client.table('agent_configs').delete().eq('client_id', '660e8400-e29b-41d4-a716-446655440000').execute()
                print("✅ Configurações de agente demo removidas")
            except Exception as e:
                print(f"⚠️  Erro ao remover agent configs: {e}")
            
            # 3. Remove demo playbooks
            try:
                result = client.table('playbooks').delete().eq('client_id', '660e8400-e29b-41d4-a716-446655440000').execute()
                print("✅ Playbooks demo removidos")
            except Exception as e:
                print(f"⚠️  Erro ao remover playbooks: {e}")
            
            # 4. Remove demo client
            try:
                result = client.table('clients').delete().eq('id', '660e8400-e29b-41d4-a716-446655440000').execute()
                print("✅ Cliente demo removido")
            except Exception as e:
                print(f"⚠️  Erro ao remover cliente: {e}")
            
            # 5. Remove demo user
            try:
                result = client.table('users').delete().eq('email', 'demo@sdr-agent.com').execute()
                print("✅ Usuário demo removido")
            except Exception as e:
                print(f"⚠️  Erro ao remover usuário demo: {e}")
            
            print("\n🎉 Limpeza concluída!")
            print("💡 Agora o sistema está limpo e pronto para uso real.")
            
        except Exception as e:
            print(f"❌ Erro ao conectar com Supabase: {e}")
    
    def main():
        """Função principal"""
        print("🚀 Removedor de Dados Demo - SDR Agent")
        print("=" * 50)
        
        remove_demo_data()
        
except ImportError:
    print("❌ Biblioteca 'supabase' não encontrada")
    print("Execute: pip3 install supabase --break-system-packages")

if __name__ == "__main__":
    main()