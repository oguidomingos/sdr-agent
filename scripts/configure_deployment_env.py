#!/usr/bin/env python3
"""
Configure deployment environment variables for Vercel
"""
import os
import json

def load_env_file():
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

def get_deployment_env_vars():
    """Get environment variables needed for deployment"""
    env_vars = load_env_file()
    
    # Required variables for deployment
    deployment_vars = {
        # Supabase Configuration
        "SUPABASE_URL": env_vars.get("SUPABASE_URL", ""),
        "SUPABASE_SERVICE_ROLE_KEY": env_vars.get("SUPABASE_SERVICE_ROLE_KEY", ""),
        
        # Authentication
        "JWT_SECRET": env_vars.get("JWT_SECRET", "dev-jwt-secret-change-in-production"),
        "JWT_EXPIRATION_HOURS": env_vars.get("JWT_EXPIRATION_HOURS", "24"),
        
        # CORS Configuration
        "CORS_ORIGINS": "https://sdr-agent-fixed.vercel.app,http://localhost:3000",
        
        # AI Configuration
        "GEMINI_API_KEY": env_vars.get("GEMINI_API_KEY", ""),
        "GEMINI_MODEL": env_vars.get("GEMINI_MODEL", "gemini-2.0-flash"),
        
        # WhatsApp Integration
        "EVOLUTION_API_URL": env_vars.get("EVOLUTION_API_URL", "http://host.docker.internal:8888"),
        "EVOLUTION_API_KEY": env_vars.get("EVOLUTION_API_KEY", ""),
        
        # Application Settings
        "ENVIRONMENT": "production",
        "DEBUG": "false",
        
        # Rate Limiting
        "RATE_LIMIT_ENABLED": "true",
        "RATE_LIMIT_CALLS": "100",
        "RATE_LIMIT_PERIOD": "3600",
    }
    
    return deployment_vars

def validate_env_vars(env_vars):
    """Validate environment variables"""
    print("🔍 Validating Environment Variables...")
    
    # Critical variables that must be present
    critical_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "JWT_SECRET"
    ]
    
    # Optional but recommended variables
    recommended_vars = [
        "GEMINI_API_KEY",
        "EVOLUTION_API_KEY"
    ]
    
    all_valid = True
    
    print("\n📋 Critical Variables:")
    for var in critical_vars:
        value = env_vars.get(var, "")
        if value:
            print(f"✅ {var}: Present")
        else:
            print(f"❌ {var}: Missing (CRITICAL)")
            all_valid = False
    
    print("\n📋 Recommended Variables:")
    for var in recommended_vars:
        value = env_vars.get(var, "")
        if value:
            print(f"✅ {var}: Present")
        else:
            print(f"⚠️  {var}: Missing (recommended)")
    
    print("\n📋 Configuration Variables:")
    config_vars = ["CORS_ORIGINS", "JWT_EXPIRATION_HOURS", "ENVIRONMENT"]
    for var in config_vars:
        value = env_vars.get(var, "")
        print(f"✅ {var}: {value}")
    
    return all_valid

def generate_vercel_env_commands(env_vars):
    """Generate Vercel CLI commands to set environment variables"""
    print("\n🚀 Vercel Environment Variable Commands:")
    print("=" * 50)
    print("# Run these commands to set environment variables in Vercel:")
    print()
    
    for key, value in env_vars.items():
        if value:  # Only include variables with values
            # Escape quotes in values
            escaped_value = value.replace('"', '\\"')
            print(f'vercel env add {key} production <<< "{escaped_value}"')
    
    print()
    print("# Or set them all at once:")
    print("vercel env pull .env.production")

def generate_env_json(env_vars):
    """Generate environment variables as JSON for manual configuration"""
    env_file = os.path.join(os.path.dirname(__file__), '..', 'deployment_env.json')
    
    # Filter out empty values
    filtered_vars = {k: v for k, v in env_vars.items() if v}
    
    with open(env_file, 'w') as f:
        json.dump(filtered_vars, f, indent=2)
    
    print(f"\n📄 Environment variables saved to: {env_file}")
    print("You can use this file to manually configure Vercel environment variables.")

def main():
    """Main configuration function"""
    print("🔧 Deployment Environment Configuration")
    print("=" * 60)
    
    # Get deployment environment variables
    env_vars = get_deployment_env_vars()
    
    # Validate variables
    is_valid = validate_env_vars(env_vars)
    
    if not is_valid:
        print("\n❌ Critical environment variables are missing!")
        print("Please ensure all critical variables are set before deployment.")
        return False
    
    # Generate Vercel commands
    generate_vercel_env_commands(env_vars)
    
    # Generate JSON file
    generate_env_json(env_vars)
    
    print("\n✅ Environment configuration completed!")
    print("\n🎯 Next Steps:")
    print("1. Run the Vercel commands above to set environment variables")
    print("2. Deploy the application to Vercel")
    print("3. Test the deployed application")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)