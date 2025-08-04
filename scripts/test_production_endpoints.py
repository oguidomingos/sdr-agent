#!/usr/bin/env python3
"""
Script para testar os endpoints em produção na Vercel
"""

import requests
import json
import sys

# URL base da aplicação em produção
BASE_URL = "https://sdr-agent-mdhjkliti-oguidomingos-projects.vercel.app"

def test_endpoint(endpoint, method="GET", data=None, headers=None):
    """Testa um endpoint específico"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"\n{'='*60}")
        print(f"Endpoint: {method} {endpoint}")
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            content = response.json()
            print(f"Response: {json.dumps(content, indent=2)}")
        except:
            print(f"Response (text): {response.text[:500]}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"Endpoint: {method} {endpoint}")
        print(f"URL: {url}")
        print(f"ERROR: {str(e)}")
        return False

def main():
    print("🚀 Testando endpoints em produção na Vercel...")
    print(f"Base URL: {BASE_URL}")
    
    # Lista de endpoints para testar
    endpoints = [
        # Endpoint raiz
        ("/", "GET"),
        ("/api", "GET"),
        
        # Health check
        ("/api/health", "GET"),
        
        # Auth endpoints
        ("/api/auth/login", "POST", {"username": "test", "password": "test"}),
        
        # Clients endpoints
        ("/api/clients", "GET"),
        
        # Messages endpoint
        ("/api/messages", "GET"),
        
        # Webhook endpoint
        ("/api/webhook", "POST", {"test": "data"}),
    ]
    
    results = []
    
    for endpoint_data in endpoints:
        endpoint = endpoint_data[0]
        method = endpoint_data[1]
        data = endpoint_data[2] if len(endpoint_data) > 2 else None
        
        success = test_endpoint(endpoint, method, data)
        results.append((endpoint, method, success))
    
    # Resumo dos resultados
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES")
    print(f"{'='*60}")
    
    success_count = 0
    for endpoint, method, success in results:
        status = "✅ OK" if success else "❌ ERRO"
        print(f"{status} {method} {endpoint}")
        if success:
            success_count += 1
    
    print(f"\n📈 Resultado: {success_count}/{len(results)} endpoints funcionando")
    
    if success_count == len(results):
        print("🎉 Todos os endpoints estão funcionando em produção!")
    else:
        print("⚠️  Alguns endpoints apresentaram problemas.")

if __name__ == "__main__":
    main()