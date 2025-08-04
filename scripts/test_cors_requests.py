#!/usr/bin/env python3
"""
Script para testar requisições CORS usando requests
"""

import subprocess
import time
import threading
import requests
import json

def start_local_server():
    """Inicia servidor local para teste"""
    print("🚀 Iniciando servidor local...")
    try:
        # Inicia o servidor FastAPI
        process = subprocess.Popen([
            "python3", "-m", "uvicorn", "api.main:app", 
            "--host", "0.0.0.0", "--port", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguarda o servidor iniciar
        time.sleep(3)
        return process
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def test_cors_headers(base_url="http://localhost:8000"):
    """Testa headers CORS"""
    print(f"\n🔍 Testando headers CORS em {base_url}")
    
    endpoints = [
        "/health",
        "/cors-config",
        "/auth/login"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        
        try:
            # Teste preflight request (OPTIONS)
            print(f"\n📋 Testando OPTIONS {endpoint}")
            options_response = requests.options(
                url,
                headers={
                    "Origin": "https://example.com",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                }
            )
            
            print(f"Status: {options_response.status_code}")
            cors_headers = {k: v for k, v in options_response.headers.items() 
                          if k.lower().startswith('access-control')}
            print(f"CORS Headers: {json.dumps(cors_headers, indent=2)}")
            
            # Teste GET request
            print(f"\n📋 Testando GET {endpoint}")
            get_response = requests.get(
                url,
                headers={"Origin": "https://example.com"}
            )
            
            print(f"Status: {get_response.status_code}")
            cors_headers = {k: v for k, v in get_response.headers.items() 
                          if k.lower().startswith('access-control')}
            print(f"CORS Headers: {json.dumps(cors_headers, indent=2)}")
            
        except Exception as e:
            print(f"❌ Erro ao testar {endpoint}: {e}")

def main():
    print("🧪 Teste de Requisições CORS")
    print("=" * 50)
    
    # Inicia servidor local
    server_process = start_local_server()
    
    if server_process:
        try:
            # Testa CORS
            test_cors_headers()
            
        finally:
            # Para o servidor
            print("\n🛑 Parando servidor...")
            server_process.terminate()
            server_process.wait()
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()