#!/usr/bin/env python3
"""
Script to test CORS configuration for the Vercel deployment
"""
import asyncio
import httpx
import json
from typing import Dict, Any

async def test_cors_preflight(base_url: str, endpoint: str) -> Dict[str, Any]:
    """Test CORS preflight request"""
    url = f"{base_url}{endpoint}"
    
    headers = {
        "Origin": "https://sdr-agent-frontend.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, Authorization"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.options(url, headers=headers)
            
            return {
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "success": response.status_code in [200, 204]
            }
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "success": False
        }

async def test_cors_actual_request(base_url: str, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test actual CORS request"""
    url = f"{base_url}{endpoint}"
    
    headers = {
        "Origin": "https://sdr-agent-frontend.vercel.app",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(url, headers=headers, json=data or {})
            else:
                response = await client.request(method, url, headers=headers, json=data or {})
            
            return {
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "cors_headers": {
                    "access_control_allow_origin": response.headers.get("access-control-allow-origin"),
                    "access_control_allow_credentials": response.headers.get("access-control-allow-credentials"),
                    "access_control_allow_methods": response.headers.get("access-control-allow-methods"),
                    "access_control_allow_headers": response.headers.get("access-control-allow-headers"),
                },
                "success": response.status_code < 500  # Any non-server error is considered success for CORS testing
            }
    except Exception as e:
        return {
            "url": url,
            "method": method,
            "error": str(e),
            "success": False
        }

async def test_health_endpoint(base_url: str) -> Dict[str, Any]:
    """Test health endpoint"""
    return await test_cors_actual_request(base_url, "/health", "GET")

async def test_auth_endpoints(base_url: str) -> Dict[str, Any]:
    """Test authentication endpoints"""
    results = {}
    
    # Test login endpoint (POST)
    login_data = {"email": "test@example.com", "password": "testpassword"}
    results["login_preflight"] = await test_cors_preflight(base_url, "/auth/login")
    results["login_actual"] = await test_cors_actual_request(base_url, "/auth/login", "POST", login_data)
    
    # Test register endpoint (POST)
    register_data = {"email": "test@example.com", "password": "testpassword", "first_name": "Test"}
    results["register_preflight"] = await test_cors_preflight(base_url, "/auth/register")
    results["register_actual"] = await test_cors_actual_request(base_url, "/auth/register", "POST", register_data)
    
    return results

async def test_clients_endpoints(base_url: str) -> Dict[str, Any]:
    """Test clients endpoints"""
    results = {}
    
    # Test clients list (GET)
    results["clients_list"] = await test_cors_actual_request(base_url, "/clients/", "GET")
    
    # Test clients create (POST)
    client_data = {"name": "Test Client", "description": "Test client for CORS testing"}
    results["clients_create_preflight"] = await test_cors_preflight(base_url, "/clients/")
    results["clients_create_actual"] = await test_cors_actual_request(base_url, "/clients/", "POST", client_data)
    
    return results

async def test_webhook_endpoint(base_url: str) -> Dict[str, Any]:
    """Test webhook endpoint"""
    webhook_data = {
        "event": "messages.upsert",
        "instance": "test_instance",
        "data": {"messages": []}
    }
    
    results = {}
    results["webhook_preflight"] = await test_cors_preflight(base_url, "/webhook/whatsapp")
    results["webhook_actual"] = await test_cors_actual_request(base_url, "/webhook/whatsapp", "POST", webhook_data)
    
    return results

def print_test_results(test_name: str, results: Dict[str, Any]):
    """Print formatted test results"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")
    
    for test_key, result in results.items():
        if isinstance(result, dict):
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"\n{status} {test_key}")
            
            if "error" in result:
                print(f"   Error: {result['error']}")
            else:
                print(f"   URL: {result.get('url', 'N/A')}")
                print(f"   Status: {result.get('status_code', 'N/A')}")
                
                if "cors_headers" in result:
                    cors_headers = result["cors_headers"]
                    print(f"   CORS Headers:")
                    for header, value in cors_headers.items():
                        if value:
                            print(f"     {header}: {value}")
        else:
            print(f"   {test_key}: {result}")

async def main():
    """Main CORS testing function"""
    print("🚀 Starting CORS testing for Vercel deployment...")
    
    # Test both local development and production URLs
    test_urls = [
        ("Local Development", "http://localhost:3000/api"),
        ("Vercel Production", "https://your-app.vercel.app/api")  # Replace with actual domain
    ]
    
    for env_name, base_url in test_urls:
        print(f"\n🌐 Testing {env_name}: {base_url}")
        
        try:
            # Test health endpoint
            health_result = await test_health_endpoint(base_url)
            print_test_results(f"Health Check - {env_name}", {"health": health_result})
            
            # Test authentication endpoints
            auth_results = await test_auth_endpoints(base_url)
            print_test_results(f"Authentication Endpoints - {env_name}", auth_results)
            
            # Test clients endpoints
            clients_results = await test_clients_endpoints(base_url)
            print_test_results(f"Clients Endpoints - {env_name}", clients_results)
            
            # Test webhook endpoint
            webhook_results = await test_webhook_endpoint(base_url)
            print_test_results(f"Webhook Endpoint - {env_name}", webhook_results)
            
        except Exception as e:
            print(f"❌ Error testing {env_name}: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 CORS testing completed!")
    print("📋 Summary:")
    print("   - Check that all endpoints return proper CORS headers")
    print("   - Verify Access-Control-Allow-Origin matches your frontend domain")
    print("   - Ensure Access-Control-Allow-Credentials is 'true' if needed")
    print("   - Confirm preflight requests (OPTIONS) return 200/204 status")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())