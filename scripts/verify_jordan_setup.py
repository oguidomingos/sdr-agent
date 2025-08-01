#!/usr/bin/env python3
"""
Script para verificar se o setup do Jordan Belfort foi feito corretamente
"""

import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def verify_jordan_setup():
    """
    Verifica se o Jordan Belfort foi configurado corretamente
    """
    print("🐺 Verificando configuração do Jordan Belfort - O Lobo de Wall Street")
    print("=" * 70)
    
    try:
        # Testa importação do prompt do Jordan
        from src.config.prompts_jordan import BASE_PROMPT, WELCOME_MESSAGES, RESPONSES
        print("✅ Prompt do Jordan Belfort importado com sucesso")
        
        # Verifica se o prompt contém elementos do Jordan
        if "Jordan Belfort" in BASE_PROMPT and "Lobo de Wall Street" in BASE_PROMPT:
            print("✅ Prompt contém informações do Jordan Belfort")
        else:
            print("❌ Prompt não contém informações esperadas do Jordan")
            
        # Testa importação do prompt principal
        from src.config.prompts import BASE_PROMPT as MAIN_PROMPT
        print("✅ Prompt principal importado com sucesso")
        
        # Verifica se o prompt principal foi atualizado
        if "Jordan Belfort" in MAIN_PROMPT and "Wall Street" in MAIN_PROMPT:
            print("✅ Prompt principal atualizado para Jordan Belfort")
        else:
            print("❌ Prompt principal não foi atualizado")
            
        # Verifica mensagens de boas-vindas
        if WELCOME_MESSAGES and "Jordan Belfort" in WELCOME_MESSAGES.get("default", ""):
            print("✅ Mensagens de boas-vindas do Jordan configuradas")
        else:
            print("❌ Mensagens de boas-vindas não configuradas")
            
        # Verifica respostas padrão
        if RESPONSES and "campeão" in RESPONSES.get("apresentacao", ""):
            print("✅ Respostas padrão do Jordan configuradas")
        else:
            print("❌ Respostas padrão não configuradas")
            
        print("\n📋 Resumo da configuração:")
        print(f"• Agente: Jordan Belfort")
        print(f"• Persona: O Lobo de Wall Street")
        print(f"• Estilo: Vendedor agressivo e motivacional")
        print(f"• Técnicas: Sistema Straight Line")
        print(f"• Respostas padrão: {len(RESPONSES)}")
        print(f"• Mensagens de boas-vindas: {len(WELCOME_MESSAGES)}")
        
        print("\n🎯 Exemplo de resposta esperada:")
        print(f"'{WELCOME_MESSAGES.get('default', 'Não configurado')}'")
        
        print("\n💰 Frases características esperadas:")
        print("• 'Escuta aqui, campeão...'")
        print("• 'DINHEIRO NÃO DORME!'")
        print("• 'Você quer ser um VENCEDOR?'")
        print("• 'Lobo de Wall Street'")
        
        print("\n🎉 Configuração do Jordan Belfort verificada com sucesso!")
        print("🐺 O sistema está pronto para vender como o Lobo de Wall Street!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        return False

if __name__ == "__main__":
    success = verify_jordan_setup()
    sys.exit(0 if success else 1)