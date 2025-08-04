#!/usr/bin/env python3
"""
Test the new deployment with fixed authentication
"""
import requests
import json

def test_new_deployment():
    """Test the new deployment"""
    api_url = "https://sdr-agent-paxa14rzk-oguidomingos-projects.vercel.app/api"
    
    print("🧪 Testing New Deployment with Fixed Authentication")
    print("=" * 70)
    print(f"API URL: {api_url}")
    
    # Test 1: Health check
    print("\n1️⃣ Testing Health Endpoint...")
    try:
        response = requests.get(f"{api_url}/health", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"   Status: {data.get('status')}")
            print(f"   Supabase: {data.get('supabase')}")
            print(f"   Version: {data.get('version')}")
            
            # Check environment variables
            env_vars = data.get('environment_vars', {})
            for var, status in env_vars.items():
                print(f"   {var}: {status}")
            
            if data.get('supabase') != 'connected':
                print("❌ Supabase not connected. Need to set environment variables.")
                return False
        else:
            print(f"❌ Health check failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Authentication
    print("\n2️⃣ Testing Authentication...")
    try:
        login_data = {
            "email": "oguigodomingos@gmail.com",
            "password": "180121430"
        }
        
        response = requests.post(f"{api_url}/auth/login", json=login_data, timeout=30)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful")
            print(f"   Token type: {token_data.get('token_type')}")
            print(f"   User ID: {token_data.get('user_id')}")
            print(f"   Email: {token_data.get('email')}")
            
            # Test 3: Get user data
            print("\n3️⃣ Testing User Data Endpoint...")
            token = token_data.get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            
            me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=30)
            print(f"User Data Status: {me_response.status_code}")
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                print("✅ User data retrieved successfully")
                print(f"   ID: {user_data.get('id')}")
                print(f"   Email: {user_data.get('email')}")
                print(f"   Name: {user_data.get('first_name')} {user_data.get('last_name')}")
                print(f"   Status: {user_data.get('status')}")
                
                # Check if it's real data
                if user_data.get('email') == 'oguigodomingos@gmail.com':
                    print("🎉 SUCCESS! Real user data returned!")
                    print("✅ Authentication is working with real Supabase data")
                    
                    # Test 4: Clients endpoint
                    print("\n4️⃣ Testing Clients Endpoint...")
                    clients_response = requests.get(f"{api_url}/clients/", headers=headers, timeout=30)
                    print(f"Clients Status: {clients_response.status_code}")
                    
                    if clients_response.status_code == 200:
                        clients_data = clients_response.json()
                        print("✅ Clients endpoint working")
                        print(f"   Total clients: {clients_data.get('total', 0)}")
                        
                        for client in clients_data.get('items', []):
                            print(f"   - {client.get('name')} ({client.get('domain')})")
                    
                    return True
                else:
                    print(f"❌ Still returning mock data: {user_data.get('email')}")
                    return False
            else:
                print(f"❌ User data failed: {me_response.text}")
                return False
        else:
            print(f"❌ Login failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

def main():
    """Main test function"""
    success = test_new_deployment()
    
    if success:
        print("\n🎉 DEPLOYMENT TEST SUCCESSFUL!")
        print("=" * 50)
        print("✅ New deployment is working correctly")
        print("✅ Real authentication with Supabase")
        print("✅ User data: Guigo Domingos (oguigodomingos@gmail.com)")
        print("\n🌐 Access URL:")
        print("https://sdr-agent-i3tkm1em8-oguidomingos-projects.vercel.app")
        print("\n🔑 Login Credentials:")
        print("Email: oguigodomingos@gmail.com")
        print("Password: 180121430")
    else:
        print("\n❌ DEPLOYMENT TEST FAILED")
        print("The deployment may need environment variables configuration.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)