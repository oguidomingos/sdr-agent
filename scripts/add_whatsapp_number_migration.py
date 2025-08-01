#!/usr/bin/env python3
"""
Migration script to add whatsapp_number column to clients table
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from src.config.settings import settings

async def run_migration():
    """Run the migration to add whatsapp_number column"""
    
    print("🔄 Starting migration: Add whatsapp_number column to clients table")
    
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            # Check if column already exists
            check_column_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'clients' 
                AND column_name = 'whatsapp_number'
            """)
            
            result = await conn.execute(check_column_query)
            existing_column = result.fetchone()
            
            if existing_column:
                print("✅ Column 'whatsapp_number' already exists in clients table")
                return
            
            # Add the column
            add_column_query = text("""
                ALTER TABLE clients 
                ADD COLUMN whatsapp_number VARCHAR(20)
            """)
            
            await conn.execute(add_column_query)
            print("✅ Added whatsapp_number column to clients table")
            
            # Create index for better performance
            create_index_query = text("""
                CREATE INDEX IF NOT EXISTS idx_clients_whatsapp_number 
                ON clients (whatsapp_number)
            """)
            
            await conn.execute(create_index_query)
            print("✅ Created index on whatsapp_number column")
            
            print("🎉 Migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())