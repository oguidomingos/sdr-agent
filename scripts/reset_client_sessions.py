#!/usr/bin/env python3
"""
Script para resetar sessões de um cliente específico
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, select
from src.config.settings import settings

async def reset_client_sessions(client_id: str):
    """Reseta todas as sessões/mensagens de um cliente"""
    
    print(f"🔄 Resetando sessões do cliente {client_id}...")
    
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Primeiro, verifica se o cliente existe
            client_query = text("""
                SELECT name FROM clients WHERE id = :client_id
            """)
            
            result = await conn.execute(client_query, {"client_id": client_id})
            client = result.fetchone()
            
            if not client:
                print(f"❌ Cliente {client_id} não encontrado")
                return
            
            print(f"📋 Cliente encontrado: {client.name}")
            
            # Conta quantas mensagens existem
            count_query = text("""
                SELECT COUNT(*) FROM messages WHERE client_id = :client_id
            """)
            
            result = await conn.execute(count_query, {"client_id": client_id})
            message_count = result.scalar()
            
            print(f"📊 Mensagens encontradas: {message_count}")
            
            if message_count == 0:
                print("✅ Nenhuma mensagem para deletar")
                return
            
            # Deleta todas as mensagens
            delete_query = text("""
                DELETE FROM messages WHERE client_id = :client_id
            """)
            
            result = await conn.execute(delete_query, {"client_id": client_id})
            
            print(f"🗑️  {result.rowcount} mensagens deletadas")
            print("✅ Sessões resetadas com sucesso!")
            print("🔄 O agente agora começará do zero para novos usuários")
            
    except Exception as e:
        print(f"❌ Erro ao resetar sessões: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python reset_client_sessions.py <client_id>")
        print("Exemplo: python reset_client_sessions.py 1d583bf9-82c8-4d2a-a0d0-63e1cff5ee4b")
        sys.exit(1)
    
    client_id = sys.argv[1]
    asyncio.run(reset_client_sessions(client_id))