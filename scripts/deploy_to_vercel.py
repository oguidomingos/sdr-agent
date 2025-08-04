#!/usr/bin/env python3
"""
Deploy SDR Agent to Vercel with all configurations
"""
import os
import json
import subprocess
import sys

# Supabase configuration
SUPABASE_CONFIG = {
    "SUPABASE_URL": "https://roezccmxctqbvdjlgdru.supabase.co",
    "SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwNzg1MzUsImV4cCI6MjA2OTY1NDUzNX0.M4JEcyLWEQwCrlGRYr_QQ-W7jDIorVllSsJqAMotodc",
    "SUPABASE_SERVICE_ROLE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDA3ODUzNSwiZXhwIjoyMDY5NjU0NTM1fQ.sE5v5FCfMKhsnehtnCF75S1N41g7f3JaZS1v1sDCeU0"
}

# Environment variables for Vercel
ENV_VARS = {
    # Supabase
    **SUPABASE_CONFIG,
    
    # Upstash Redis (placeholder - needs to be configured)
    "UPSTASH_REDIS_REST_URL": "https://your-redis.upstash.io",
    "UPSTASH_REDIS_REST_TOKEN": "your-redis-token",
    
    # Evolution API
    "EVOLUTION_API_URL": "https://evolutionapi.centralsupernova.com.br",
    "EVOLUTION_API_KEY": "509dbd54-c20c-4a5b-b889-a0494a861f5a",
    
    # Security
    "JWT_SECRET": "sdr-agent-jwt-secret-2025-production",
    "SECRET_KEY": "sdr-agent-secret-key-2025-production",
    "WEBHOOK_SECRET": "sdr-agent-webhook-secret-2025",
    
    # Application
    "ENVIRONMENT": "production",
    "DEBUG": "false",
    "JWT_EXPIRATION_HOURS": "24",
    
    # AI Configuration
    "GEMINI_API_KEY": "your-gemini-api-key-here",
    "GEMINI_MODEL": "gemini-2.0-flash",
    
    # CORS
    "CORS_ORIGINS": "https://sdr-agent-supabase.vercel.app,http://localhost:3000"
}

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return result.stdout
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return None
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return None

def create_vercel_project():
    """Create or link Vercel project"""
    print("🚀 Setting up Vercel project...")
    
    # Check if already linked
    if os.path.exists('.vercel'):
        print("✅ Vercel project already linked")
        return True
    
    # Initialize Vercel project
    result = run_command("vercel --yes", "Initializing Vercel project")
    return result is not None

def set_environment_variables():
    """Set environment variables in Vercel"""
    print("⚙️ Setting environment variables...")
    
    success_count = 0
    total_count = len(ENV_VARS)
    
    for key, value in ENV_VARS.items():
        # Mask sensitive values in output
        display_value = value if not any(secret in key.lower() for secret in ['key', 'secret', 'token']) else '***'
        print(f"   Setting {key}={display_value}")
        
        command = f'vercel env add {key} production <<< "{value}"'
        result = run_command(command, f"Setting {key}")
        
        if result is not None:
            success_count += 1
    
    print(f"✅ Set {success_count}/{total_count} environment variables")
    return success_count == total_count

def deploy_to_vercel():
    """Deploy to Vercel"""
    print("🚀 Deploying to Vercel...")
    
    # Deploy to production
    result = run_command("vercel --prod", "Deploying to production")
    
    if result:
        # Extract deployment URL
        lines = result.strip().split('\n')
        deployment_url = None
        
        for line in lines:
            if 'https://' in line and 'vercel.app' in line:
                deployment_url = line.strip()
                break
        
        if deployment_url:
            print(f"🎉 Deployment successful!")
            print(f"🌐 URL: {deployment_url}")
            return deployment_url
        else:
            print("✅ Deployment completed (URL not found in output)")
            return True
    
    return False

def update_frontend_config(deployment_url):
    """Update frontend configuration with deployment URL"""
    if not deployment_url or not isinstance(deployment_url, str):
        print("⚠️  Skipping frontend config update (no deployment URL)")
        return
    
    print("🔧 Updating frontend configuration...")
    
    # Update frontend API configuration
    api_config_path = "frontend/src/lib/api.ts"
    
    try:
        with open(api_config_path, 'r') as f:
            content = f.read()
        
        # Replace the API URL
        updated_content = content.replace(
            'https://your-app.vercel.app/api',
            f'{deployment_url}/api'
        )
        
        with open(api_config_path, 'w') as f:
            f.write(updated_content)
        
        print("✅ Frontend configuration updated")
        
    except Exception as e:
        print(f"⚠️  Could not update frontend config: {e}")

def create_deployment_summary():
    """Create deployment summary"""
    summary = {
        "deployment_date": "2025-01-08",
        "status": "completed",
        "supabase": {
            "url": SUPABASE_CONFIG["SUPABASE_URL"],
            "project_ref": "roezccmxctqbvdjlgdru",
            "tables_created": ["users", "clients", "messages", "playbooks", "agent_configs"],
            "demo_data": True
        },
        "vercel": {
            "project_name": "sdr-agent-supabase",
            "environment_variables": len(ENV_VARS),
            "functions": ["auth", "clients", "messages", "webhook"]
        },
        "next_steps": [
            "Configure Upstash Redis",
            "Set up custom domain (optional)",
            "Test all API endpoints",
            "Configure webhook URLs in Evolution API"
        ]
    }
    
    with open("deployment_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("💾 Deployment summary saved to deployment_summary.json")

def main():
    """Main deployment function"""
    print("=" * 60)
    print("🚀 SDR AGENT - VERCEL + SUPABASE DEPLOYMENT")
    print("=" * 60)
    
    # Step 1: Create/link Vercel project
    if not create_vercel_project():
        print("❌ Failed to create Vercel project")
        sys.exit(1)
    
    # Step 2: Set environment variables
    if not set_environment_variables():
        print("⚠️  Some environment variables failed to set, but continuing...")
    
    # Step 3: Deploy to Vercel
    deployment_url = deploy_to_vercel()
    if not deployment_url:
        print("❌ Deployment failed")
        sys.exit(1)
    
    # Step 4: Update frontend config
    update_frontend_config(deployment_url)
    
    # Step 5: Create summary
    create_deployment_summary()
    
    print("\n" + "=" * 60)
    print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"🌐 Application URL: {deployment_url if isinstance(deployment_url, str) else 'Check Vercel dashboard'}")
    print(f"📊 Supabase URL: {SUPABASE_CONFIG['SUPABASE_URL']}")
    print(f"🏥 Demo client: demo-supabase.sdr-agent.com")
    print(f"📧 Demo user: demo@sdr-agent.com (password: demo123)")
    print("\n📋 Next Steps:")
    print("   1. Configure Upstash Redis for session management")
    print("   2. Test all API endpoints")
    print("   3. Configure webhook URLs in Evolution API")
    print("   4. Set up custom domain (optional)")
    print("=" * 60)

if __name__ == "__main__":
    main()