#!/usr/bin/env python3
"""
Deploy script for fixed authentication implementation
"""
import os
import subprocess
import json
import time

def run_command(command, cwd=None):
    """Run shell command and return result"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def load_env_vars():
    """Load environment variables from .env file"""
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    env_vars = {}
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"').strip("'")
    
    return env_vars

def set_vercel_env_vars():
    """Set environment variables in Vercel"""
    print("🔧 Setting Vercel Environment Variables...")
    
    env_vars = load_env_vars()
    
    # Critical environment variables for deployment
    deployment_vars = {
        "SUPABASE_URL": env_vars.get("SUPABASE_URL", ""),
        "SUPABASE_SERVICE_ROLE_KEY": env_vars.get("SUPABASE_SERVICE_ROLE_KEY", ""),
        "JWT_SECRET": "production-jwt-secret-2025-sdr-agent",
        "JWT_EXPIRATION_HOURS": "24",
        "CORS_ORIGINS": "*",  # Allow all origins for now
        "GEMINI_API_KEY": env_vars.get("GEMINI_API_KEY", ""),
        "GEMINI_MODEL": "gemini-2.0-flash",
        "EVOLUTION_API_URL": env_vars.get("EVOLUTION_API_URL", ""),
        "EVOLUTION_API_KEY": env_vars.get("EVOLUTION_API_KEY", ""),
        "ENVIRONMENT": "production",
        "DEBUG": "false"
    }
    
    # Validate critical variables
    critical_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
    missing_vars = [var for var in critical_vars if not deployment_vars[var]]
    
    if missing_vars:
        print(f"❌ Missing critical environment variables: {missing_vars}")
        return False
    
    # Set each environment variable
    success_count = 0
    for key, value in deployment_vars.items():
        if value:  # Only set non-empty values
            print(f"Setting {key}...")
            success, stdout, stderr = run_command(f'vercel env add {key} production', cwd='..')
            
            if success:
                # Provide the value via stdin simulation
                success2, stdout2, stderr2 = run_command(f'echo "{value}" | vercel env add {key} production', cwd='..')
                if success2:
                    print(f"✅ {key} set successfully")
                    success_count += 1
                else:
                    print(f"❌ Failed to set {key}: {stderr2}")
            else:
                print(f"❌ Failed to set {key}: {stderr}")
    
    print(f"✅ Set {success_count}/{len([v for v in deployment_vars.values() if v])} environment variables")
    return success_count > 0

def deploy_to_vercel():
    """Deploy application to Vercel"""
    print("\n🚀 Deploying to Vercel...")
    
    # Deploy command
    success, stdout, stderr = run_command('vercel --prod --yes', cwd='..')
    
    if success:
        print("✅ Deployment successful!")
        
        # Extract deployment URL from output
        lines = stdout.split('\n')
        deployment_url = None
        
        for line in lines:
            if 'https://' in line and 'vercel.app' in line:
                deployment_url = line.strip()
                break
        
        if deployment_url:
            print(f"🌐 Deployment URL: {deployment_url}")
            return deployment_url
        else:
            print("⚠️  Deployment successful but URL not found in output")
            return "https://sdr-agent-fixed.vercel.app"  # Default URL
    else:
        print(f"❌ Deployment failed: {stderr}")
        return None

def test_deployment(deployment_url):
    """Test the deployed application"""
    print(f"\n🧪 Testing deployment: {deployment_url}")
    
    import requests
    
    try:
        # Test health endpoint
        health_url = f"{deployment_url}/api/health"
        response = requests.get(health_url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            
            # Check Supabase connection
            supabase_status = data.get('supabase', 'unknown')
            if supabase_status == 'connected':
                print("✅ Supabase connection working")
            else:
                print(f"❌ Supabase connection issue: {supabase_status}")
                return False
            
            # Test authentication
            print("\n🔐 Testing authentication...")
            login_data = {
                "email": "oguigodomingos@gmail.com",
                "password": "180121430"
            }
            
            auth_response = requests.post(f"{deployment_url}/api/auth/login", json=login_data, timeout=30)
            
            if auth_response.status_code == 200:
                print("✅ Login working")
                
                token_data = auth_response.json()
                token = token_data.get('access_token')
                
                if token:
                    # Test /auth/me
                    headers = {"Authorization": f"Bearer {token}"}
                    me_response = requests.get(f"{deployment_url}/api/auth/me", headers=headers, timeout=30)
                    
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        print("✅ User data endpoint working")
                        
                        # Check for real data
                        if user_data.get('email') == 'oguigodomingos@gmail.com':
                            print("✅ Real user data returned!")
                            print(f"   Name: {user_data.get('first_name')} {user_data.get('last_name')}")
                            print(f"   Email: {user_data.get('email')}")
                            return True
                        else:
                            print(f"❌ Still returning mock data: {user_data.get('email')}")
                            return False
                    else:
                        print(f"❌ /auth/me failed: {me_response.status_code}")
                        return False
                else:
                    print("❌ No token in login response")
                    return False
            else:
                print(f"❌ Login failed: {auth_response.status_code}")
                return False
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Fixed Authentication Deployment Script")
    print("=" * 60)
    
    # Step 1: Set environment variables
    if not set_vercel_env_vars():
        print("❌ Failed to set environment variables. Aborting deployment.")
        return False
    
    # Step 2: Deploy to Vercel
    deployment_url = deploy_to_vercel()
    if not deployment_url:
        print("❌ Deployment failed. Aborting.")
        return False
    
    # Step 3: Wait a bit for deployment to be ready
    print("\n⏳ Waiting for deployment to be ready...")
    time.sleep(30)
    
    # Step 4: Test deployment
    if test_deployment(deployment_url):
        print(f"\n🎉 DEPLOYMENT SUCCESSFUL!")
        print("=" * 40)
        print(f"✅ URL: {deployment_url}")
        print(f"✅ Authentication: Working with real data")
        print(f"✅ User: Guigo Domingos (oguigodomingos@gmail.com)")
        print("\n🎯 You can now access the application and see your real data!")
        return True
    else:
        print(f"\n❌ Deployment completed but tests failed")
        print(f"URL: {deployment_url}")
        print("Check the deployment logs for issues.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)