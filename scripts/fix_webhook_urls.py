#!/usr/bin/env python3
"""
Script para corrigir URLs de webhook que ficaram com /temp
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
from src.core.evolution_integration import evolution_service

async def fix_webhook_urls():
    """Corrige URLs de webhook que ficaram com /temp"""
    
    print("🔄 Iniciando correção de URLs de webhook...")
    
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Busca clientes com webhook_url contendo /temp
            query = text("""
                SELECT id, name, webhook_url, evolution_instance, 
                       evolution_api_url, evolution_api_key
                FROM clients 
                WHERE webhook_url LIKE '%/temp%'
            """)
            
            result = await conn.execute(query)
            clients_to_fix = result.fetchall()
            
            if not clients_to_fix:
                print("✅ Nenhum cliente com webhook /temp encontrado")
                return
            
            print(f"🔧 Encontrados {len(clients_to_fix)} clientes para corrigir:")
            
            for client in clients_to_fix:
                print(f"  - {client.name} (ID: {client.id})")
                print(f"    URL atual: {client.webhook_url}")
                
                # Gera nova URL correta
                new_webhook_url = client.webhook_url.replace("/temp", f"/{client.id}")
                print(f"    Nova URL: {new_webhook_url}")
                
                # Atualiza no banco de dados
                update_query = text("""
                    UPDATE clients 
                    SET webhook_url = :new_url 
                    WHERE id = :client_id
                """)
                
                await conn.execute(update_query, {
                    "new_url": new_webhook_url,
                    "client_id": client.id
                })
                
                # Atualiza na Evolution API se as credenciais estiverem disponíveis
                if client.evolution_instance and client.evolution_api_url and client.evolution_api_key:
                    try:
                        await evolution_service.update_webhook_url(
                            instance_name=client.evolution_instance,
                            webhook_url=new_webhook_url,
                            evolution_url=client.evolution_api_url,
                            evolution_key=client.evolution_api_key
                        )
                        print(f"    ✅ Webhook atualizado na Evolution API")
                    except Exception as e:
                        print(f"    ⚠️  Falha ao atualizar na Evolution API: {e}")
                else:
                    print(f"    ⚠️  Credenciais Evolution não disponíveis, apenas banco atualizado")
                
                print()
            
            print(f"🎉 Correção concluída! {len(clients_to_fix)} clientes atualizados.")
            
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_webhook_urls())