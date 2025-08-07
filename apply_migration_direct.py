#!/usr/bin/env python3
"""Apply migration directly to Supabase production using SQL execution"""

import os
from supabase import create_client, Client

def apply_migration_direct():
    try:
        # Connect to Supabase
        supabase_url = 'https://roezccmxctqbvdjlgdru.supabase.co'
        # Use service role key for admin operations
        service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDA3ODUzNSwiZXhwIjoyMDY5NjU0NTM1fQ.sE5v5FCfMKhsnehtnCF75S1N41g7f3JaZS1v1sDCeU0')
        
        print(f"🔗 Connecting to Supabase with service role...")
        supabase: Client = create_client(supabase_url, service_key)
        
        # Create the table directly with SQL
        create_table_sql = """
        -- Create message cooldown table
        CREATE TABLE IF NOT EXISTS message_cooldown (
            user_phone VARCHAR(50) PRIMARY KEY,
            client_id UUID REFERENCES clients(id) ON DELETE CASCADE NOT NULL,
            last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_processed_at TIMESTAMP WITH TIME ZONE,
            pending_messages JSONB DEFAULT '[]'::jsonb,
            cooldown_seconds INTEGER DEFAULT 90,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Create indexes for performance
        CREATE INDEX IF NOT EXISTS idx_message_cooldown_client ON message_cooldown(client_id);
        CREATE INDEX IF NOT EXISTS idx_message_cooldown_last_message ON message_cooldown(last_message_at);
        CREATE INDEX IF NOT EXISTS idx_message_cooldown_last_processed ON message_cooldown(last_processed_at);

        -- Enable RLS
        ALTER TABLE message_cooldown ENABLE ROW LEVEL SECURITY;

        -- Create RLS policy
        DROP POLICY IF EXISTS "Message cooldown accessible by all" ON message_cooldown;
        CREATE POLICY "Message cooldown accessible by all" ON message_cooldown
            FOR ALL USING (true);

        -- Add updated_at trigger
        DROP TRIGGER IF EXISTS update_message_cooldown_updated_at ON message_cooldown;
        CREATE TRIGGER update_message_cooldown_updated_at BEFORE UPDATE ON message_cooldown
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
        
        print("📄 Executing migration SQL...")
        
        # Execute using raw SQL via rpc
        result = supabase.rpc('exec', {'sql': create_table_sql}).execute()
        
        print("✅ Migration executed successfully!")
        
        # Test the table
        print("🧪 Testing table access...")
        test_result = supabase.table('message_cooldown').select('*').limit(1).execute()
        print("✅ Table is accessible!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Try alternative method - direct table creation
        try:
            print("🔄 Trying alternative method...")
            
            # Simple table creation without complex SQL
            supabase.table('message_cooldown').insert({
                'user_phone': 'test_phone',
                'client_id': '550e8400-e29b-41d4-a716-446655440000',  # Dummy UUID
                'last_message_at': '2025-08-06T23:00:00Z',
                'pending_messages': []
            }).execute()
            
        except Exception as e2:
            print(f"❌ Alternative method failed: {e2}")
            print("ℹ️ Will create table schema manually...")
            
        return False

if __name__ == "__main__":
    apply_migration_direct()