#!/usr/bin/env python3
"""
Test Supabase connection and verify data
"""
import os
import asyncio
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://roezccmxctqbvdjlgdru.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDA3ODUzNSwiZXhwIjoyMDY5NjU0NTM1fQ.sE5v5FCfMKhsnehtnCF75S1N41g7f3JaZS1v1sDCeU0"

async def test_supabase_connection():
    """Test Supabase connection and data"""
    print("🚀 Testing Supabase connection...")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Test 1: Check users table
        print("\n📊 Testing users table...")
        users_result = supabase.table('users').select('*').execute()
        print(f"   ✅ Users found: {len(users_result.data)}")
        
        if users_result.data:
            user = users_result.data[0]
            print(f"   📧 Demo user: {user['email']}")
        
        # Test 2: Check clients table
        print("\n🏢 Testing clients table...")
        clients_result = supabase.table('clients').select('*').execute()
        print(f"   ✅ Clients found: {len(clients_result.data)}")
        
        if clients_result.data:
            client = clients_result.data[0]
            print(f"   🏥 Demo client: {client['name']}")
            print(f"   🌐 Domain: {client['domain']}")
        
        # Test 3: Check messages table
        print("\n💬 Testing messages table...")
        messages_result = supabase.table('messages').select('*').execute()
        print(f"   ✅ Messages found: {len(messages_result.data)}")
        
        # Test 4: Check playbooks table
        print("\n📖 Testing playbooks table...")
        playbooks_result = supabase.table('playbooks').select('*').execute()
        print(f"   ✅ Playbooks found: {len(playbooks_result.data)}")
        
        # Test 5: Check agent_configs table
        print("\n🤖 Testing agent_configs table...")
        configs_result = supabase.table('agent_configs').select('*').execute()
        print(f"   ✅ Agent configs found: {len(configs_result.data)}")
        
        print("\n🎉 All tests passed! Supabase is ready for use.")
        
        return {
            "status": "success",
            "users": len(users_result.data),
            "clients": len(clients_result.data),
            "messages": len(messages_result.data),
            "playbooks": len(playbooks_result.data),
            "agent_configs": len(configs_result.data)
        }
        
    except Exception as e:
        print(f"❌ Error testing Supabase: {e}")
        return {"status": "error", "error": str(e)}

async def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 SUPABASE CONNECTION TEST")
    print("=" * 60)
    
    result = await test_supabase_connection()
    
    print("\n" + "=" * 60)
    if result["status"] == "success":
        print("✅ SUPABASE SETUP COMPLETED SUCCESSFULLY!")
        print(f"📊 Database URL: {SUPABASE_URL}")
        print(f"🏥 Demo client ready for testing")
        print(f"📧 Demo user: demo@sdr-agent.com (password: demo123)")
    else:
        print("❌ SUPABASE SETUP FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())