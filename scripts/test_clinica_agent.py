#!/usr/bin/env python3
"""
Script para testar o novo agente de clínica
"""

import asyncio
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.gemini import GeminiClient
from src.types.schemas import GeminiRequest, SessionContext, MessageContext

async def test_clinica_agent():
    """
    Testa o agente de clínica com diferentes cenários
    """
    print("🏥 Testando Agente de Clínica - Maria da Clínica Vida Saudável")
    print("=" * 60)
    
    try:
        # Inicializa o cliente Gemini
        gemini_client = GeminiClient()
        
        # Cenários de teste
        test_scenarios = [
            {
                "name": "Saudação inicial",
                "message": "Oi",
                "expected_keywords": ["Maria", "Clínica Vida Saudável", "ajudar"]
            },
            {
                "name": "Pergunta sobre especialidades",
                "message": "Quais especialidades vocês têm?",
                "expected_keywords": ["especialidades", "Cardiologia", "Dermatologia"]
            },
            {
                "name": "Interesse em consulta",
                "message": "Preciso marcar uma consulta com cardiologista",
                "expected_keywords": ["cardiologia", "agendar", "consulta"]
            },
            {
                "name": "Pergunta sobre valores",
                "message": "Quanto custa a consulta?",
                "expected_keywords": ["R$", "180", "consulta"]
            },
            {
                "name": "Objeção de preço",
                "message": "Está muito caro",
                "expected_keywords": ["desconto", "150", "saúde"]
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🧪 Teste {i}: {scenario['name']}")
            print(f"📝 Mensagem: {scenario['message']}")
            
            # Cria contexto de sessão
            session = SessionContext(
                session_id=f"test_session_{i}",
                client_id="test_client",
                messages=[
                    MessageContext(
                        content=scenario['message'],
                        timestamp="2024-01-01T10:00:00",
                        metadata={"from_me": False}
                    )
                ],
                metadata={
                    "name": "João",
                    "phone": "11999999999"
                }
            )
            
            # Processa a mensagem
            response = await gemini_client.process_session(
                session=session,
                user_message=scenario['message']
            )
            
            if response:
                print(f"🤖 Resposta: {response.content}")
                
                # Verifica se contém palavras-chave esperadas
                response_lower = response.content.lower()
                found_keywords = [kw for kw in scenario['expected_keywords'] 
                                if kw.lower() in response_lower]
                
                if found_keywords:
                    print(f"✅ Palavras-chave encontradas: {found_keywords}")
                else:
                    print(f"⚠️  Nenhuma palavra-chave esperada encontrada")
                    print(f"   Esperadas: {scenario['expected_keywords']}")
            else:
                print("❌ Erro: Nenhuma resposta gerada")
            
            print("-" * 50)
        
        print("\n🎉 Teste do agente de clínica concluído!")
        print("📋 O agente Maria está configurado e respondendo como recepcionista da clínica")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_clinica_agent())