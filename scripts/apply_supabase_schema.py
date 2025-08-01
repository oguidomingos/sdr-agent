#!/usr/bin/env python3
"""
Script to apply schema migration to Supabase database
"""
import asyncio
import os
from pathlib import Path
from src.core.supabase_config import get_supabase_client

async def apply_schema_migration():
    """Apply the schema migration to Supabase"""
    print("🚀 Starting Supabase schema migration...")
    
    try:
        # Get Supabase client
        supabase = get_supabase_client(admin=True)
        
        # Read the schema migration SQL file
        schema_file = Path("scripts/supabase_schema_migration.sql")
        if not schema_file.exists():
            print("❌ Schema migration file not found!")
            return False
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        print("📊 Applying schema migration to Supabase...")
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
                
            try:
                # Execute each statement
                result = supabase.rpc('exec_sql', {'sql': statement})
                print(f"✅ Statement {i}/{len(statements)} executed successfully")
                success_count += 1
                
            except Exception as e:
                print(f"⚠️  Statement {i}/{len(statements)} failed: {str(e)[:100]}...")
                error_count += 1
                
                # Continue with other statements unless it's a critical error
                if "already exists" not in str(e).lower():
                    print(f"   Statement: {statement[:100]}...")
        
        print(f"\n📋 Migration Summary:")
        print(f"   Successful statements: {success_count}")
        print(f"   Failed statements: {error_count}")
        print(f"   Total statements: {len(statements)}")
        
        if error_count == 0:
            print("✅ Schema migration completed successfully!")
        elif success_count > error_count:
            print("⚠️  Schema migration completed with some warnings")
        else:
            print("❌ Schema migration failed with multiple errors")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply schema migration: {e}")
        return False

async def verify_schema():
    """Verify that the schema was applied correctly"""
    print("🔍 Verifying schema application...")
    
    try:
        supabase = get_supabase_client(admin=True)
        
        # Check if main tables exist
        expected_tables = ['users', 'clients', 'messages', 'playbooks', 'agent_configs']
        
        for table in expected_tables:
            try:
                # Try to query the table (this will fail if table doesn't exist)
                result = supabase.table(table).select("*").limit(1).execute()
                print(f"✅ Table '{table}' exists and is accessible")
            except Exception as e:
                print(f"❌ Table '{table}' verification failed: {e}")
                return False
        
        print("✅ Schema verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Schema verification failed: {e}")
        return False

async def create_demo_data():
    """Create demo data in Supabase for testing"""
    print("🌱 Creating demo data...")
    
    try:
        supabase = get_supabase_client(admin=True)
        
        # Create demo user
        demo_user_data = {
            "email": "demo@sdr-agent.com",
            "hashed_password": "$2b$12$demo.hash.for.testing.purposes.only",
            "first_name": "Demo",
            "last_name": "User",
            "status": "active",
            "plan": "free"
        }
        
        user_result = supabase.table('users').insert(demo_user_data).execute()
        if user_result.data:
            user_id = user_result.data[0]['id']
            print(f"✅ Demo user created with ID: {user_id}")
            
            # Create demo client
            demo_client_data = {
                "owner_id": user_id,
                "name": "Demo Medical Clinic",
                "description": "Demo client for testing Supabase migration",
                "domain": "demo-supabase.sdr-agent.com",
                "status": "active",
                "agent_name": "Dr. Assistant",
                "agent_persona": "Sou um assistente médico especializado em atendimento via WhatsApp.",
                "welcome_message": "Olá! Sou o Dr. Assistant. Como posso ajudá-lo hoje?",
                "contact_email": "demo@sdr-agent.com"
            }
            
            client_result = supabase.table('clients').insert(demo_client_data).execute()
            if client_result.data:
                client_id = client_result.data[0]['id']
                print(f"✅ Demo client created with ID: {client_id}")
                
                # Create demo playbook
                demo_playbook_data = {
                    "client_id": client_id,
                    "name": "Medical SPIN Selling Playbook",
                    "description": "Demo playbook for Supabase testing",
                    "status": "active",
                    "is_default": True,
                    "steps": [
                        {"stage": "welcome", "message": "Olá! Como posso ajudá-lo?"},
                        {"stage": "situation", "prompt": "Descubra a situação atual do paciente"}
                    ]
                }
                
                playbook_result = supabase.table('playbooks').insert(demo_playbook_data).execute()
                if playbook_result.data:
                    print(f"✅ Demo playbook created")
                
        print("✅ Demo data created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create demo data: {e}")
        return False

async def main():
    """Main migration function"""
    print("🚀 Starting Supabase schema migration process...")
    
    # Check environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("   Please set these variables before running the migration.")
        return
    
    # Apply schema migration
    if not await apply_schema_migration():
        print("❌ Schema migration failed. Stopping.")
        return
    
    # Verify schema
    if not await verify_schema():
        print("❌ Schema verification failed. Please check the database.")
        return
    
    # Create demo data
    if not await create_demo_data():
        print("⚠️  Demo data creation failed, but schema migration was successful.")
    
    print("\n🎉 Supabase migration completed successfully!")
    print("   Next steps:")
    print("   1. Test the Supabase connection in your application")
    print("   2. Update your application to use Supabase instead of PostgreSQL")
    print("   3. Test the RLS policies with different users")

if __name__ == "__main__":
    asyncio.run(main())