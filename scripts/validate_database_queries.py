#!/usr/bin/env python3
"""
Database query validation script for Supabase integration
"""
import os
import sys
import asyncio

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def load_env_file():
    """Load environment variables from .env file"""
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")

# Load environment
load_env_file()

async def validate_database_connection():
    """Validate Supabase database connection"""
    print("🔍 Validating Database Connection...")
    
    try:
        from src.core.supabase_db import get_supabase_db
        
        # Test connection
        db = get_supabase_db()
        print("✅ Database connection established")
        
        # Test health check
        is_healthy = await db.health_check()
        if is_healthy:
            print("✅ Database health check passed")
        else:
            print("❌ Database health check failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def validate_user_queries():
    """Validate user-related database queries"""
    print("\n👤 Validating User Queries...")
    
    try:
        from src.core.supabase_db import get_supabase_db
        db = get_supabase_db()
        
        # Test user lookup by email
        test_email = "oguigodomingos@gmail.com"
        user = await db.get_user_by_email(test_email)
        
        if user:
            print(f"✅ User found by email: {test_email}")
            print(f"   ID: {user.get('id')}")
            print(f"   Name: {user.get('first_name')} {user.get('last_name')}")
            print(f"   Status: {user.get('status')}")
            
            # Test user lookup by ID
            user_by_id = await db.get_user_by_id(user['id'])
            if user_by_id:
                print(f"✅ User found by ID: {user['id']}")
                
                # Validate data consistency
                if user_by_id['email'] == user['email']:
                    print("✅ User data consistency check passed")
                else:
                    print("❌ User data consistency check failed")
                    return False
            else:
                print(f"❌ User not found by ID: {user['id']}")
                return False
                
            # Validate user data format
            required_fields = ['id', 'email', 'first_name', 'last_name', 'status', 'plan']
            missing_fields = [field for field in required_fields if field not in user]
            
            if not missing_fields:
                print("✅ User data format validation passed")
            else:
                print(f"❌ User data missing fields: {missing_fields}")
                return False
                
            # Check for mock data
            if user['email'] == 'user@example.com' or user['first_name'] == 'Demo':
                print("❌ Database contains mock data")
                return False
            else:
                print("✅ No mock data detected in database")
                
            return user
            
        else:
            print(f"❌ User not found: {test_email}")
            return False
            
    except Exception as e:
        print(f"❌ User query validation failed: {e}")
        return False

async def validate_client_queries(user_data):
    """Validate client-related database queries"""
    print("\n🏢 Validating Client Queries...")
    
    if not user_data:
        print("❌ No user data available for client validation")
        return False
    
    try:
        from src.core.supabase_db import get_supabase_db
        db = get_supabase_db()
        
        user_id = user_data['id']
        
        # Test get clients by owner
        clients = await db.get_clients_by_owner(user_id)
        print(f"✅ Clients query executed for user {user_id}")
        print(f"   Found {len(clients)} clients")
        
        for client in clients:
            print(f"   - {client.get('name', 'Unknown')} ({client.get('domain', 'Unknown')})")
            
            # Validate client data format
            required_fields = ['id', 'name', 'domain', 'owner_id', 'status']
            missing_fields = [field for field in required_fields if field not in client]
            
            if missing_fields:
                print(f"❌ Client data missing fields: {missing_fields}")
                return False
            
            # Validate owner relationship
            if client['owner_id'] != user_id:
                print(f"❌ Client owner mismatch: expected {user_id}, got {client['owner_id']}")
                return False
        
        print("✅ Client queries validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Client query validation failed: {e}")
        return False

async def validate_authentication_flow():
    """Validate complete authentication flow"""
    print("\n🔐 Validating Authentication Flow...")
    
    try:
        from api.auth.router import verify_password, create_access_token
        import jwt
        
        # Test password verification
        test_password = "180121430"
        # This is a bcrypt hash of "180121430" for testing
        test_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvQSG"
        
        if verify_password(test_password, test_hash):
            print("✅ Password verification working")
        else:
            print("❌ Password verification failed")
            return False
        
        # Test JWT token creation
        test_user_id = "test-user-123"
        test_email = "test@example.com"
        
        token = create_access_token(test_user_id, test_email)
        if token:
            print("✅ JWT token creation working")
            
            # Test token decoding
            JWT_SECRET = os.environ.get("JWT_SECRET", "your-jwt-secret-here")
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
                if payload.get('user_id') == test_user_id and payload.get('email') == test_email:
                    print("✅ JWT token validation working")
                else:
                    print("❌ JWT token payload validation failed")
                    return False
            except jwt.JWTError as e:
                print(f"❌ JWT token decoding failed: {e}")
                return False
        else:
            print("❌ JWT token creation failed")
            return False
        
        print("✅ Authentication flow validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Authentication flow validation failed: {e}")
        return False

async def validate_environment_variables():
    """Validate required environment variables"""
    print("\n🌍 Validating Environment Variables...")
    
    required_vars = {
        "SUPABASE_URL": "Supabase database URL",
        "SUPABASE_SERVICE_ROLE_KEY": "Supabase service role key",
        "JWT_SECRET": "JWT signing secret"
    }
    
    all_present = True
    
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: Present ({description})")
            # Don't print the actual value for security
        else:
            print(f"❌ {var}: Missing ({description})")
            all_present = False
    
    if all_present:
        print("✅ All required environment variables present")
    else:
        print("❌ Some required environment variables are missing")
    
    return all_present

async def main():
    """Main validation function"""
    print("🧪 Database Query Validation Suite")
    print("=" * 60)
    
    # Step 1: Validate environment variables
    env_valid = await validate_environment_variables()
    if not env_valid:
        print("\n❌ Environment validation failed. Cannot proceed.")
        return False
    
    # Step 2: Validate database connection
    db_connected = await validate_database_connection()
    if not db_connected:
        print("\n❌ Database connection failed. Cannot proceed.")
        return False
    
    # Step 3: Validate user queries
    user_data = await validate_user_queries()
    if not user_data:
        print("\n❌ User query validation failed.")
        return False
    
    # Step 4: Validate client queries
    clients_valid = await validate_client_queries(user_data)
    if not clients_valid:
        print("\n❌ Client query validation failed.")
        return False
    
    # Step 5: Validate authentication flow
    auth_valid = await validate_authentication_flow()
    if not auth_valid:
        print("\n❌ Authentication flow validation failed.")
        return False
    
    print("\n🎉 ALL VALIDATIONS PASSED!")
    print("✅ Database queries are working correctly")
    print("✅ Real user data is being returned")
    print("✅ No mock data detected")
    print("✅ Authentication flow is functional")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Validation suite failed: {e}")
        sys.exit(1)