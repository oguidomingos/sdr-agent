#!/usr/bin/env python3
"""
Script para testar CORS em produção na Vercel
"""

import subprocess
import json

def test_cors_headers(url):
    """Testa headers CORS usando curl"""
    print(f"🔍 Testando CORS em: {url}")
    
    # Teste preflight request (OPTIONS)
    print(f"\n📋 Testando OPTIONS request...")
    
    cmd = [
        "curl", "-s", "-I", "-X", "OPTIONS",
        "-H", "Origin: https://example.com",
        "-H", "Access-Control-Request-Method: POST",
        "-H", "Access-Control-Request-Headers: Content-Type",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        print(f"Status Code: {result.returncode}")
        print("Headers:")
        
        # Procura por headers CORS
        cors_headers = []
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.lower().startswith('access-control'):
                cors_headers.append(line)
                print(f"  ✅ {line}")
        
        if not cors_headers:
            print("  ❌ Nenhum header CORS encontrado")
            print("Headers completos:")
            print(result.stdout)
        
        return len(cors_headers) > 0
        
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
        return False

def test_multiple_urls():
    """Testa múltiplas URLs da Vercel"""
    urls = [
        "https://sdr-agent-hln7g9sdj-oguidomingos-projects.vercel.app/api/health",
        "https://sdr-agent-hln7g9sdj-oguidomingos-projects.vercel.app/api/cors-config",
        "https://sdr-agent-hln7g9sdj-oguidomingos-projects.vercel.app/api/auth/login"
    ]
    
    results = []
    
    for url in urls:
        print(f"\n{'='*60}")
        success = test_cors_headers(url)
        results.append((url, success))
    
    # Resumo
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES CORS")
    print(f"{'='*60}")
    
    success_count = 0
    for url, success in results:
        status = "✅ OK" if success else "❌ ERRO"
        endpoint = url.split('/')[-1] if '/' in url else url
        print(f"{status} {endpoint}")
        if success:
            success_count += 1
    
    print(f"\n📈 Resultado: {success_count}/{len(results)} endpoints com CORS funcionando")
    
    if success_count > 0:
        print("🎉 CORS está funcionando em alguns endpoints!")
    else:
        print("⚠️  CORS não está funcionando em nenhum endpoint.")

def main():
    print("🚀 Teste de CORS em Produção na Vercel")
    print("=" * 60)
    
    test_multiple_urls()
    
    print("\n✅ Testes concluídos!")
    print("\nNota: Se a aplicação estiver protegida por autenticação da Vercel,")
    print("os headers CORS podem não aparecer até que você faça login.")

if __name__ == "__main__":
    main()