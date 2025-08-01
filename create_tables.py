#!/usr/bin/env python3
"""
Script para criar tabelas manualmente no banco de dados
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from src.core.db import Base
from src.config.settings import settings

async def create_tables():
    """Cria as tabelas no banco de dados"""
    print("🔗 Conectando ao banco de dados...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        print("📊 Criando tabelas...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Tabelas criadas com sucesso!")
        
        # Verificar se as tabelas foram criadas
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Tabelas no banco: {tables}")
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())