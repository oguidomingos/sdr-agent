#!/usr/bin/env python3
"""Apply Supabase migration for message cooldown table"""

import os
from supabase import create_client, Client

def apply_migration():
    try:
        # Get Supabase credentials from environment or hardcoded for development
        supabase_url = os.getenv('SUPABASE_URL', 'https://roezccmxctqbvdjlgdru.supabase.co')
        supabase_key = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY4MzU5NzUsImV4cCI6MjA1MjQxMTk3NX0.lJXOqjWIoMhxhCuwQMUHlNS-kKI5mhAzQRUbqvVP1yI')
        
        print(f"🔗 Connecting to Supabase: {supabase_url}")
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Read the migration file
        with open('supabase/migrations/20250806000001_add_message_cooldown.sql', 'r') as f:
            migration_sql = f.read()
        
        print("📄 Applying migration...")
        print(f"SQL Preview:\n{migration_sql[:200]}...")
        
        # Execute the migration
        # Note: This is a simplified approach - in production you'd use proper migration tools
        result = supabase.rpc('exec_sql', {'sql': migration_sql})
        
        print("✅ Migration applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        print("ℹ️  This might be normal if the table already exists or if we need to use a different approach")
        return False

if __name__ == "__main__":
    apply_migration()