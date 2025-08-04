#!/usr/bin/env python3
"""
Script para testar configuração CORS localmente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.cors_config import get_cors_config, is_vercel_environment, get_vercel_origins

def test_cors_config():
    """Testa a configuração CORS"""
    print("🔧 Testando configuração CORS...")
    print(f"Ambiente Vercel: {is_vercel_environment()}")
    
    # Testa configuração CORS
    config = get_cors_config()
    print(f"\n📋 Configuração CORS:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Testa origens Vercel
    if is_vercel_environment():
        vercel_origins = get_vercel_origins()
        print(f"\n🌐 Origens Vercel detectadas:")
        for origin in vercel_origins:
            print(f"  - {origin}")
    
    # Testa variáveis de ambiente
    print(f"\n🔍 Variáveis de ambiente relevantes:")
    env_vars = ["VERCEL", "VERCEL_URL", "CORS_ORIGINS"]
    for var in env_vars:
        value = os.environ.get(var, "não definida")
        print(f"  {var}: {value}")

def simulate_vercel_environment():
    """Simula ambiente Vercel para teste"""
    print("\n🧪 Simulando ambiente Vercel...")
    
    # Define variáveis de ambiente do Vercel
    os.environ["VERCEL"] = "1"
    os.environ["VERCEL_URL"] = "sdr-agent-test123-oguidomingos-projects.vercel.app"
    
    # Testa novamente
    test_cors_config()

def main():
    print("🚀 Teste de Configuração CORS")
    print("=" * 50)
    
    # Teste em ambiente local
    print("\n1. Ambiente Local:")
    test_cors_config()
    
    # Teste simulando Vercel
    print("\n" + "=" * 50)
    print("2. Simulação Ambiente Vercel:")
    simulate_vercel_environment()
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main()