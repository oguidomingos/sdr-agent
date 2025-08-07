#!/usr/bin/env python3
"""Create message_cooldown table directly via Supabase Client"""

import os
from supabase import create_client
import asyncio

def create_message_cooldown_table():
    try:
        # Connect to Supabase
        supabase_url = 'https://roezccmxctqbvdjlgdru.supabase.co'
        service_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDA3ODUzNSwiZXhwIjoyMDY5NjU0NTM1fQ.sE5v5FCfMKhsnehtnCF75S1N41g7f3JaZS1v1sDCeU0'
        
        print(f"🔗 Connecting to Supabase...")
        supabase = create_client(supabase_url, service_key)
        
        # Test basic connection first
        print("🧪 Testing connection...")
        try:
            result = supabase.table('clients').select('id').limit(1).execute()
            print("✅ Connected to Supabase successfully!")
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
        
        # Check if table already exists
        print("🔍 Checking if message_cooldown table exists...")
        try:
            existing_result = supabase.table('message_cooldown').select('user_phone').limit(1).execute()
            print("✅ Table message_cooldown already exists!")
            return True
        except Exception as e:
            print(f"📋 Table doesn't exist yet, will create it. Error: {e}")
        
        # Create table using PostgreSQL raw SQL via edge function or directly
        # Since we can't create tables via the Supabase client directly,
        # let's inform the user they need to execute the SQL in Supabase console
        
        migration_sql = """
-- Add message cooldown system for database-based cooldown management
-- This replaces the threading.Timer approach for serverless compatibility

CREATE TABLE message_cooldown (
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
CREATE INDEX idx_message_cooldown_client ON message_cooldown(client_id);
CREATE INDEX idx_message_cooldown_last_message ON message_cooldown(last_message_at);
CREATE INDEX idx_message_cooldown_last_processed ON message_cooldown(last_processed_at);

-- Enable RLS
ALTER TABLE message_cooldown ENABLE ROW LEVEL SECURITY;

-- RLS Policy for message cooldown (accessible by webhook - no auth required for API calls)
CREATE POLICY "Message cooldown accessible by all" ON message_cooldown
    FOR ALL USING (true);

-- Add updated_at trigger
CREATE TRIGGER update_message_cooldown_updated_at BEFORE UPDATE ON message_cooldown
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add helpful functions for cooldown management
CREATE OR REPLACE FUNCTION should_process_message(
    p_user_phone VARCHAR(50),
    p_cooldown_seconds INTEGER DEFAULT 90
) RETURNS BOOLEAN AS $$
DECLARE
    last_msg_time TIMESTAMP WITH TIME ZONE;
    time_diff_seconds INTEGER;
BEGIN
    -- Get the last message timestamp
    SELECT last_message_at INTO last_msg_time
    FROM message_cooldown
    WHERE user_phone = p_user_phone;
    
    -- If no record exists, should process (first message)
    IF last_msg_time IS NULL THEN
        RETURN TRUE;
    END IF;
    
    -- Calculate time difference in seconds
    time_diff_seconds := EXTRACT(EPOCH FROM (NOW() - last_msg_time));
    
    -- Return true if cooldown period has passed
    RETURN time_diff_seconds >= p_cooldown_seconds;
END;
$$ LANGUAGE plpgsql;
"""
        
        print("📋 Please execute this SQL in your Supabase SQL Editor:")
        print("=" * 80)
        print(migration_sql)
        print("=" * 80)
        
        # Alternative: create a minimal record to test if table creation works
        print("\n🆕 Attempting to create a test record (this will fail if table doesn't exist)...")
        try:
            test_record = {
                'user_phone': 'test_migration_check',
                'client_id': '00000000-0000-0000-0000-000000000000',  # This will fail due to FK constraint, but that's OK
                'pending_messages': []
            }
            result = supabase.table('message_cooldown').insert(test_record).execute()
            print("✅ Table exists and is accessible!")
            
            # Clean up test record
            supabase.table('message_cooldown').delete().eq('user_phone', 'test_migration_check').execute()
            
        except Exception as e:
            print(f"❌ Table creation needed: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_message_cooldown_table()