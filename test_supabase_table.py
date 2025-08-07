#!/usr/bin/env python3
"""Test message_cooldown table directly with same credentials as app"""

import os
from supabase import create_client

def test_table_access():
    try:
        # Use same credentials as the app
        supabase_url = 'https://roezccmxctqbvdjlgdru.supabase.co'
        # Try both keys
        service_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDA3ODUzNSwiZXhwIjoyMDY5NjU0NTM1fQ.sE5v5FCfMKhsnehtnCF75S1N41g7f3JaZS1v1sDCeU0'
        anon_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwNzg1MzUsImV4cCI6MjA2OTY1NDUzNX0.M4JEcyLWEQwCrlGRYr_QQ-W7jDIorVllSsJqAMotodc'
        
        print("🔗 Testing with service role key...")
        supabase = create_client(supabase_url, service_key)
        
        # Test the exact query from the error
        try:
            result = supabase.table('message_cooldown').select('last_message_at,last_processed_at').eq('user_phone', '5561936180578@s.whatsapp.net').execute()
            print(f"✅ Service role query successful: {len(result.data)} rows")
        except Exception as e:
            print(f"❌ Service role query failed: {e}")
        
        print("\n🔗 Testing with anon key...")
        supabase_anon = create_client(supabase_url, anon_key)
        
        try:
            result = supabase_anon.table('message_cooldown').select('last_message_at,last_processed_at').eq('user_phone', '5561936180578@s.whatsapp.net').execute()
            print(f"✅ Anon key query successful: {len(result.data)} rows")
        except Exception as e:
            print(f"❌ Anon key query failed: {e}")
            
        # Test table existence
        print("\n🔍 Testing table existence...")
        try:
            result = supabase.table('message_cooldown').select('*').limit(1).execute()
            print(f"✅ Table exists - found {len(result.data)} rows")
        except Exception as e:
            print(f"❌ Table check failed: {e}")
            
        # Check what tables exist
        print("\n📋 Checking available tables...")
        try:
            # This might not work with standard Supabase client
            # Let's try listing clients table instead
            result = supabase.table('clients').select('id').limit(1).execute()
            print(f"✅ Clients table accessible - found {len(result.data)} rows")
        except Exception as e:
            print(f"❌ Clients table check failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_table_access()