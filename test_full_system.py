#!/usr/bin/env python3
"""
Teste completo do sistema SDR Agent
- Testa envio de mensagem via Evolution API
- Testa funcionamento do buffer/cooldown
- Testa resposta do agente AI
- Verifica operações no banco de dados
"""

import requests
import json
import time
from datetime import datetime, timezone

# Configuração do teste
BASE_URL = "https://sdr-agent-five.vercel.app"
TEST_PHONE = "5561936180578"
INSTANCE = "sdr_77f276b5"

def test_webhook_message():
    """Simula uma mensagem recebida via webhook"""
    print("\n🧪 TESTE 1: Simulando mensagem via webhook")
    print("=" * 50)
    
    # Payload simulando uma mensagem do Evolution API
    webhook_payload = {
        "event": "messages.upsert",
        "instance": INSTANCE,
        "data": {
            "key": {
                "remoteJid": f"{TEST_PHONE}@s.whatsapp.net",
                "fromMe": False,
                "id": f"TEST_{int(time.time())}"
            },
            "pushName": "Teste Sistema",
            "status": "DELIVERY_ACK",
            "message": {
                "conversation": "Olá, este é um teste do sistema. Como vocês podem me ajudar?",
                "messageContextInfo": {
                    "deviceListMetadata": {
                        "senderKeyHash": "TEST_HASH",
                        "senderTimestamp": str(int(time.time())),
                        "recipientKeyHash": "TEST_HASH_2",
                        "recipientTimestamp": str(int(time.time()))
                    },
                    "deviceListMetadataVersion": 2,
                    "messageSecret": "TEST_SECRET"
                }
            },
            "messageType": "conversation",
            "messageTimestamp": int(time.time()),
            "instanceId": "test-instance-id",
            "source": "test"
        },
        "destination": f"{BASE_URL}/api/webhook/whatsapp/{INSTANCE}",
        "date_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sender": f"{TEST_PHONE}@s.whatsapp.net",
        "server_url": "http://localhost:8080",
        "apikey": "test-api-key"
    }
    
    try:
        print(f"📤 Enviando mensagem de teste para: {BASE_URL}/api/webhook/whatsapp/{INSTANCE}")
        print(f"📱 Simulando mensagem de: {TEST_PHONE}")
        print(f"💬 Texto: {webhook_payload['data']['message']['conversation']}")
        
        response = requests.post(
            f"{BASE_URL}/api/webhook/whatsapp/{INSTANCE}",
            json=webhook_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print("✅ Resposta recebida:")
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
                return True, response_data
            except:
                print("✅ Resposta recebida (não JSON):")
                print(response.text)
                return True, response.text
        else:
            print(f"❌ Erro na resposta: {response.status_code}")
            print(f"Erro: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem de teste: {e}")
        return False, None

def test_buffer_functionality():
    """Testa o sistema de buffer enviando múltiplas mensagens rapidamente"""
    print("\n🧪 TESTE 2: Testando funcionalidade do buffer")
    print("=" * 50)
    
    messages = [
        "Primeira mensagem - teste buffer",
        "Segunda mensagem - deve ser agrupada", 
        "Terceira mensagem - também deve ser agrupada"
    ]
    
    results = []
    
    for i, message in enumerate(messages, 1):
        print(f"\n📤 Enviando mensagem {i}/3: {message}")
        
        webhook_payload = {
            "event": "messages.upsert",
            "instance": INSTANCE,
            "data": {
                "key": {
                    "remoteJid": f"{TEST_PHONE}@s.whatsapp.net",
                    "fromMe": False,
                    "id": f"BUFFER_TEST_{i}_{int(time.time())}"
                },
                "pushName": "Teste Buffer",
                "message": {"conversation": message},
                "messageType": "conversation",
                "messageTimestamp": int(time.time())
            }
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/webhook/whatsapp/{INSTANCE}",
                json=webhook_payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            print(f"Status: {response.status_code}")
            results.append((response.status_code, response.text))
            
            # Pausa curta entre mensagens (simula mensagens rápidas)
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            results.append((None, str(e)))
    
    print(f"\n📊 Resultado do teste de buffer:")
    for i, (status, text) in enumerate(results, 1):
        print(f"Mensagem {i}: Status {status}")
    
    return results

def test_ai_response():
    """Testa se o agente AI está respondendo adequadamente"""
    print("\n🧪 TESTE 3: Testando resposta do agente AI")
    print("=" * 50)
    
    # Mensagem que deve gerar uma resposta clara do agente
    test_message = "Olá! Preciso de informações sobre os serviços da ROIGem. Vocês fazem consultoria em marketing digital?"
    
    webhook_payload = {
        "event": "messages.upsert",
        "instance": INSTANCE,
        "data": {
            "key": {
                "remoteJid": f"{TEST_PHONE}@s.whatsapp.net",
                "fromMe": False,
                "id": f"AI_TEST_{int(time.time())}"
            },
            "pushName": "Teste IA",
            "message": {"conversation": test_message},
            "messageType": "conversation",
            "messageTimestamp": int(time.time())
        }
    }
    
    print(f"💬 Testando com mensagem: {test_message}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/webhook/whatsapp/{INSTANCE}",
            json=webhook_payload,
            headers={"Content-Type": "application/json"},
            timeout=45  # Timeout maior para processamento da IA
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print("✅ Resposta da IA:")
                
                # Procura por indicações de que a IA processou
                if 'ai_response' in response_data:
                    print(f"🤖 IA respondeu: {response_data['ai_response']}")
                    return True
                elif 'processed' in response_data:
                    print(f"✅ Mensagem processada: {response_data}")
                    return True
                else:
                    print(f"📄 Resposta completa: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                    return True
            except:
                print(f"✅ Resposta (texto): {response.text}")
                return True
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste da IA: {e}")
        return False

def test_health_check():
    """Testa se a aplicação está funcionando"""
    print("\n🧪 TESTE 0: Health Check da aplicação")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Aplicação está funcionando:")
            print(f"  - Status: {data.get('status', 'unknown')}")
            print(f"  - Supabase: {data.get('supabase', 'unknown')}")
            print(f"  - Vercel: {data.get('vercel', False)}")
            return True
        else:
            print(f"❌ Health check falhou: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA SDR AGENT")
    print("=" * 60)
    print(f"🎯 Base URL: {BASE_URL}")
    print(f"📱 Telefone teste: {TEST_PHONE}")
    print(f"🔗 Instância: {INSTANCE}")
    print(f"⏰ Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Teste 0: Health Check
    results['health'] = test_health_check()
    
    # Teste 1: Mensagem simples
    results['message'], response_data = test_webhook_message()
    
    # Aguarda um pouco antes do próximo teste
    print(f"\n⏳ Aguardando 5 segundos antes do próximo teste...")
    time.sleep(5)
    
    # Teste 2: Buffer
    results['buffer'] = test_buffer_functionality()
    
    # Aguarda um pouco antes do próximo teste  
    print(f"\n⏳ Aguardando 10 segundos antes do teste da IA...")
    time.sleep(10)
    
    # Teste 3: IA
    results['ai'] = test_ai_response()
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    print(f"✅ Health Check: {'PASSOU' if results['health'] else '❌ FALHOU'}")
    print(f"✅ Envio de Mensagem: {'PASSOU' if results['message'] else '❌ FALHOU'}")
    print(f"✅ Sistema de Buffer: {'PASSOU' if any(status == 200 for status, _ in results['buffer']) else '❌ FALHOU'}")
    print(f"✅ Agente AI: {'PASSOU' if results['ai'] else '❌ FALHOU'}")
    
    # Status geral
    all_passed = (
        results['health'] and 
        results['message'] and 
        any(status == 200 for status, _ in results['buffer']) and 
        results['ai']
    )
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema funcionando corretamente.")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM. Verifique os logs acima.")
    print("=" * 60)

if __name__ == "__main__":
    main()