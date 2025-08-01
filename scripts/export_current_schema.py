#!/usr/bin/env python3
"""
Script to export current PostgreSQL schema and data for migration to Supabase
"""
import asyncio
import json
import os
from datetime import datetime
from sqlalchemy import text
from src.core.db import engine, AsyncSessionLocal
from src.core.db import User, Client, Message, Playbook, AgentConfig

async def export_schema_info():
    """Export current schema information"""
    print("🔍 Exporting current PostgreSQL schema information...")
    
    schema_info = {
        "export_date": datetime.utcnow().isoformat(),
        "tables": {},
        "indexes": {},
        "constraints": {}
    }
    
    try:
        async with engine.connect() as conn:
            # Get table information
            tables_query = text("""
                SELECT table_name, column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
            """)
            
            result = await conn.execute(tables_query)
            for row in result:
                table_name = row[0]
                if table_name not in schema_info["tables"]:
                    schema_info["tables"][table_name] = []
                
                schema_info["tables"][table_name].append({
                    "column_name": row[1],
                    "data_type": row[2],
                    "is_nullable": row[3],
                    "column_default": row[4]
                })
            
            # Get indexes
            indexes_query = text("""
                SELECT schemaname, tablename, indexname, indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname;
            """)
            
            result = await conn.execute(indexes_query)
            for row in result:
                table_name = row[1]
                if table_name not in schema_info["indexes"]:
                    schema_info["indexes"][table_name] = []
                
                schema_info["indexes"][table_name].append({
                    "index_name": row[2],
                    "definition": row[3]
                })
            
            # Get foreign key constraints
            fk_query = text("""
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    tc.constraint_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public';
            """)
            
            result = await conn.execute(fk_query)
            for row in result:
                table_name = row[0]
                if table_name not in schema_info["constraints"]:
                    schema_info["constraints"][table_name] = []
                
                schema_info["constraints"][table_name].append({
                    "column_name": row[1],
                    "foreign_table": row[2],
                    "foreign_column": row[3],
                    "constraint_name": row[4]
                })
    
    except Exception as e:
        print(f"❌ Error exporting schema: {e}")
        return None
    
    # Save schema info to file
    with open("scripts/current_schema_export.json", "w") as f:
        json.dump(schema_info, f, indent=2, default=str)
    
    print("✅ Schema information exported to scripts/current_schema_export.json")
    return schema_info

async def export_sample_data():
    """Export sample data for testing migration"""
    print("📊 Exporting sample data...")
    
    sample_data = {
        "export_date": datetime.utcnow().isoformat(),
        "users": [],
        "clients": [],
        "messages": [],
        "playbooks": [],
        "agent_configs": []
    }
    
    try:
        async with AsyncSessionLocal() as session:
            # Export users (limit to 5 for sample)
            from sqlalchemy import select
            
            users_result = await session.execute(select(User).limit(5))
            users = users_result.scalars().all()
            
            for user in users:
                sample_data["users"].append({
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "status": user.status.value if user.status else None,
                    "plan": user.plan,
                    "max_clients": user.max_clients,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                })
            
            # Export clients (limit to 10 for sample)
            clients_result = await session.execute(select(Client).limit(10))
            clients = clients_result.scalars().all()
            
            for client in clients:
                sample_data["clients"].append({
                    "id": client.id,
                    "owner_id": client.owner_id,
                    "name": client.name,
                    "domain": client.domain,
                    "status": client.status.value if client.status else None,
                    "agent_name": client.agent_name,
                    "created_at": client.created_at.isoformat() if client.created_at else None
                })
            
            # Export recent messages (limit to 50)
            messages_result = await session.execute(
                select(Message).order_by(Message.timestamp.desc()).limit(50)
            )
            messages = messages_result.scalars().all()
            
            for message in messages:
                sample_data["messages"].append({
                    "id": message.id,
                    "client_id": message.client_id,
                    "user_id": message.user_id,
                    "content": message.content[:100] + "..." if len(message.content) > 100 else message.content,
                    "message_direction": message.message_direction.value if message.message_direction else None,
                    "timestamp": message.timestamp.isoformat() if message.timestamp else None
                })
    
    except Exception as e:
        print(f"❌ Error exporting sample data: {e}")
        return None
    
    # Save sample data to file
    with open("scripts/sample_data_export.json", "w") as f:
        json.dump(sample_data, f, indent=2, default=str)
    
    print("✅ Sample data exported to scripts/sample_data_export.json")
    return sample_data

async def main():
    """Main export function"""
    print("🚀 Starting schema and data export...")
    
    # Export schema information
    schema_info = await export_schema_info()
    if not schema_info:
        print("❌ Failed to export schema information")
        return
    
    # Export sample data
    sample_data = await export_sample_data()
    if not sample_data:
        print("❌ Failed to export sample data")
        return
    
    print("\n📋 Export Summary:")
    print(f"   Tables found: {len(schema_info['tables'])}")
    print(f"   Sample users: {len(sample_data['users'])}")
    print(f"   Sample clients: {len(sample_data['clients'])}")
    print(f"   Sample messages: {len(sample_data['messages'])}")
    
    print("\n✅ Export completed successfully!")
    print("   Next steps:")
    print("   1. Review scripts/current_schema_export.json")
    print("   2. Review scripts/sample_data_export.json")
    print("   3. Run the Supabase schema migration")

if __name__ == "__main__":
    asyncio.run(main())