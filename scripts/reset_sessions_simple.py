#!/usr/bin/env python3
"""
Script simples para resetar sessões de clientes
Remove arquivos de sessão e limpa cache
"""

import os
import shutil
import json
from pathlib import Path

def reset_sessions():
    """
    Reseta todas as sessões de clientes
    """
    print("🔄 Iniciando reset das sessões...")
    
    # Diretórios que podem conter dados de sessão
    session_dirs = [
        "data/sessions",
        "data/clients", 
        "data/cache",
        "temp",
        ".cache"
    ]
    
    # Arquivos de sessão que podem existir
    session_files = [
        "sessions.json",
        "clients.json",
        "cache.json"
    ]
    
    reset_count = 0
    
    # Remove diretórios de sessão
    for dir_path in session_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Removido diretório: {dir_path}")
                reset_count += 1
            except Exception as e:
                print(f"⚠️  Erro ao remover {dir_path}: {e}")
    
    # Remove arquivos de sessão
    for file_path in session_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Removido arquivo: {file_path}")
                reset_count += 1
            except Exception as e:
                print(f"⚠️  Erro ao remover {file_path}: {e}")
    
    # Procura por arquivos .json que podem ser sessões
    for json_file in Path(".").glob("**/*.json"):
        if any(keyword in str(json_file).lower() for keyword in ["session", "client", "cache"]):
            try:
                os.remove(json_file)
                print(f"✅ Removido arquivo de sessão: {json_file}")
                reset_count += 1
            except Exception as e:
                print(f"⚠️  Erro ao remover {json_file}: {e}")
    
    # Cria estrutura básica se necessário
    os.makedirs("data", exist_ok=True)
    
    print(f"\n🎉 Reset concluído! {reset_count} itens removidos.")
    print("📋 Sessões resetadas - sistema pronto para novo agente de clínica")
    
    return True

if __name__ == "__main__":
    reset_sessions()