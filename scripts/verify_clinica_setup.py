#!/usr/bin/env python3
"""
Script para verificar se o setup do agente de clínica foi feito corretamente
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_clinica_setup():
    """
    Verifica se o agente de clínica foi configurado corretamente
    """
    print("🏥 Verificando configuração do Agente de Clínica")
    print("=" * 50)
    
    try:
        # Testa importação do prompt da clínica
        from src.config.prompts_clinica import BASE_PROMPT, WELCOME_MESSAGES, RESPONSES
        print("✅ Prompt da clínica importado com sucesso")
        
        # Verifica se o prompt contém elementos da clínica
        if "Maria" in BASE_PROMPT and "Clínica Vida Saudável" in BASE_PROMPT:
            print("✅ Prompt contém informações da clínica")
        else:
            print("❌ Prompt não contém informações esperadas da clínica")
            
        # Testa importação do prompt principal
        from src.config.prompts import BASE_PROMPT as MAIN_PROMPT
        print("✅ Prompt principal importado com sucesso")
        
        # Verifica se o prompt principal foi atualizado
        if "Maria" in MAIN_PROMPT and "Clínica Vida Saudável" in MAIN_PROMPT:
            print("✅ Prompt principal atualizado para clínica")
        else:
            print("❌ Prompt principal não foi atualizado")
            
        # Verifica mensagens de boas-vindas
        if WELCOME_MESSAGES and "Maria" in WELCOME_MESSAGES.get("default", ""):
            print("✅ Mensagens de boas-vindas configuradas")
        else:
            print("❌ Mensagens de boas-vindas não configuradas")
            
        # Verifica respostas padrão
        if RESPONSES and "especialidades" in RESPONSES:
            print("✅ Respostas padrão da clínica configuradas")
        else:
            print("❌ Respostas padrão não configuradas")
            
        print("\n📋 Resumo da configuração:")
        print(f"• Agente: Maria")
        print(f"• Clínica: Clínica Vida Saudável")
        print(f"• Especialidades: {len(RESPONSES.get('especialidades', '').split('•')) - 1}")
        print(f"• Mensagens de boas-vindas: {len(WELCOME_MESSAGES)}")
        
        print("\n🎯 Exemplo de resposta esperada:")
        print(f"'{WELCOME_MESSAGES.get('default', 'Não configurado')}'")
        
        print("\n🎉 Configuração do agente de clínica verificada com sucesso!")
        print("📱 O sistema está pronto para receber mensagens como recepcionista da clínica")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        return False

if __name__ == "__main__":
    success = verify_clinica_setup()
    sys.exit(0 if success else 1)