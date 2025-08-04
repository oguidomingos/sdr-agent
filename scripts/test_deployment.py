#!/usr/bin/env python3
"""
Test the deployed application on Vercel
"""
import asyncio
import httpx
import json

DEPLOYMENT_URL = "https://sdr-agent-fzxylmlvo-oguidomingos-projects.vercel.app"

async def test_health_endpoint():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DEPLOYMENT_URL}/api/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check passed: {data['status']}")
                print(f"   📊 Version: {data['version']}")
                print(f"   🌍 Environment: {data['environment']}")
                return True
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

async def test_cors():
    """Test CORS configuration"""
    print("🌐 Testing CORS configuration...")
    
    try:
        headers = {
            "Origin": "https://sdr-agent-fzxylmlvo-oguidomingos-projects.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type, Authorization"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.options(f"{DEPLOYMENT_URL}/api/health", headers=headers)
            
            cors_headers = {
                "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
                "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
                "access-control-allow-headers": response.headers.get("access-control-allow-headers"),
            }
            
            print(f"   ✅ CORS preflight status: {response.status_code}")
            for header, value in cors_headers.items():
                if value:
                    print(f"   📋 {header}: {value}")
            
            return response.status_code in [200, 204]
            
    except Exception as e:
        print(f"   ❌ CORS test error: {e}")
        return False

async def test_auth_endpoints():
    """Test authentication endpoints"""
    print("🔐 Testing authentication endpoints...")
    
    try:
        # Test registration endpoint
        async with httpx.AsyncClient() as client:
            register_data = {
                "email": "test@example.com",
                "password": "testpassword123",
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = await client.post(
                f"{DEPLOYMENT_URL}/api/auth/register",
                json=register_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201, 400]:  # 400 might be "user already exists"
                print(f"   ✅ Registration endpoint responding: {response.status_code}")
            else:
                print(f"   ⚠️  Registration endpoint status: {response.status_code}")
            
            # Test login endpoint
            login_data = {
                "email": "demo@sdr-agent.com",
                "password": "demo123"
            }
            
            response = await client.post(
                f"{DEPLOYMENT_URL}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Login successful for demo user")
                print(f"   🎫 Token type: {data.get('token_type', 'N/A')}")
                return True
            else:
                print(f"   ⚠️  Login status: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"   ❌ Auth test error: {e}")
        return False

async def test_supabase_connection():
    """Test Supabase connection through API"""
    print("📊 Testing Supabase connection...")
    
    try:
        # Login first to get token
        async with httpx.AsyncClient() as client:
            login_data = {
                "email": "demo@sdr-agent.com",
                "password": "demo123"
            }
            
            login_response = await client.post(
                f"{DEPLOYMENT_URL}/api/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code != 200:
                print(f"   ⚠️  Could not login to test Supabase connection")
                return False
            
            token_data = login_response.json()
            token = token_data.get('access_token')
            
            if not token:
                print(f"   ⚠️  No access token received")
                return False
            
            # Test clients endpoint
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = await client.get(
                f"{DEPLOYMENT_URL}/api/clients/",
                headers=headers
            )
            
            if response.status_code == 200:
                clients = response.json()
                print(f"   ✅ Supabase connection working")
                print(f"   🏥 Clients found: {len(clients)}")
                return True
            else:
                print(f"   ⚠️  Clients endpoint status: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ Supabase test error: {e}")
        return False

async def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 VERCEL DEPLOYMENT TEST")
    print("=" * 60)
    print(f"🌐 Testing: {DEPLOYMENT_URL}")
    print("=" * 60)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("CORS Configuration", test_cors),
        ("Authentication", test_auth_endpoints),
        ("Supabase Connection", test_supabase_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        result = await test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED! Deployment is successful!")
    elif passed >= len(tests) * 0.75:
        print("⚠️  Most tests passed. Deployment is mostly working.")
    else:
        print("❌ Multiple tests failed. Please check the deployment.")
    
    print("\n📋 Next Steps:")
    print("   1. Configure Upstash Redis for session management")
    print("   2. Set up webhook URLs in Evolution API")
    print("   3. Test WhatsApp integration")
    print("   4. Configure custom domain (optional)")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())