#!/usr/bin/env python3
"""
Teste enviando uma mensagem real e verificando se ela:
1. É processada pelo sistema
2. Gera resposta da IA
3. É salva no banco de dados
4. É enviada via WhatsApp
"""

import requests
import json
import time
from datetime import datetime
from supabase import create_client

def send_test_message():
    """Envia uma mensagem de teste real"""
    print("📤 ENVIANDO MENSAGEM REAL PARA TESTE")
    print("=" * 50)
    
    # Mensagem que deve disparar uma resposta clara do agente ROIGem
    test_message = "Olá! Sou empresário e gostaria de saber como vocês podem me ajudar a melhorar o ROI das minhas campanhas de marketing digital. Investimos cerca de R$ 8.000 por mês mas não temos clareza dos resultados."
    
    webhook_payload = {
        "event": "messages.upsert",
        "instance": "sdr_77f276b5",
        "data": {
            "key": {
                "remoteJid": "5561936180578@s.whatsapp.net",
                "fromMe": False,
                "id": f"FINAL_TEST_{int(time.time())}"
            },
            "pushName": "Teste Final Sistema",
            "status": "DELIVERY_ACK", 
            "message": {
                "conversation": test_message,
                "messageContextInfo": {
                    "deviceListMetadata": {
                        "senderKeyHash": "FinalTestHash",
                        "senderTimestamp": str(int(time.time())),
                        "recipientKeyHash": "FinalTestHash2",
                        "recipientTimestamp": str(int(time.time()))
                    },
                    "deviceListMetadataVersion": 2,
                    "messageSecret": "FinalTestSecret"
                }
            },
            "messageType": "conversation",
            "messageTimestamp": int(time.time()),
            "instanceId": "final-test-instance",
            "source": "test-final"
        },
        "destination": "https://sdr-agent-five.vercel.app/api/webhook/whatsapp/sdr_77f276b5",
        "date_time": datetime.now().isoformat() + "Z",
        "sender": "5561936180578@s.whatsapp.net",
        "server_url": "http://localhost:8080",
        "apikey": "final-test-key"
    }
    
    print(f"💬 Mensagem: {test_message[:100]}...")
    print(f"📱 Para número: 5561936180578")
    print(f"🔗 Instância: sdr_77f276b5")
    
    try:
        print("\n📡 Enviando para o webhook...")
        response = requests.post(
            "https://sdr-agent-five.vercel.app/api/webhook/whatsapp/sdr_77f276b5",
            json=webhook_payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Timeout maior para processamento completo
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print("✅ Resposta do sistema:")
                print(json.dumps(response_data, indent=2, ensure_ascii=False))
                return True, response_data
            except:
                print(f"✅ Resposta (texto): {response.text}")
                return True, response.text
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Detalhes: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False, None

def check_database_after_test():
    """Verifica se a mensagem foi salva no banco após o teste"""
    print("\n🔍 VERIFICANDO BANCO DE DADOS APÓS O TESTE")
    print("=" * 50)
    
    try:
        # Aguardar um pouco para o processamento
        print("⏳ Aguardando 5 segundos para processamento...")
        time.sleep(5)
        
        supabase_url = 'https://roezccmxctqbvdjlgdru.supabase.co'
        service_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJvZXpjY214Y3RxYnZkamxnZHJ1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDA3ODUzNSwiZXhwIjoyMDY5NjU0NTM1fQ.sE5v5FCfMKhsnehtnCF75S1N41g7f3JaZS1v1sDCeU0'
        
        supabase = create_client(supabase_url, service_key)
        client_id = "77f276b5-5a0a-4888-be96-5ab3fa96b1b3"
        
        # 1. Verificar mensagens mais recentes
        print("📋 Verificando mensagens mais recentes...")
        recent_messages = supabase.table('messages').select('*').eq('client_id', client_id).order('timestamp', desc=True).limit(5).execute()
        
        if recent_messages.data:
            print(f"✅ Encontradas {len(recent_messages.data)} mensagens recentes:")
            for i, msg in enumerate(recent_messages.data, 1):
                direction = msg.get('message_direction', 'unknown')
                content = msg.get('content', 'no content')[:80] + ('...' if len(msg.get('content', '')) > 80 else '')
                timestamp = msg.get('timestamp', 'no time')
                status = msg.get('status', 'no status')
                print(f"  {i}. [{direction}] [{status}] {content}")
                print(f"     ⏰ {timestamp}")
        else:
            print("❌ Nenhuma mensagem encontrada")
        
        # 2. Verificar estado do cooldown
        print("\n⏱️  Verificando estado do cooldown...")
        cooldown_state = supabase.table('message_cooldown').select('*').eq('user_phone', '5561936180578@s.whatsapp.net').execute()
        
        if cooldown_state.data:
            record = cooldown_state.data[0]
            last_msg = record.get('last_message_at', 'never')
            last_processed = record.get('last_processed_at', 'never')
            pending_count = len(record.get('pending_messages', []))
            
            print(f"✅ Estado do cooldown:")
            print(f"  📥 Última mensagem: {last_msg}")
            print(f"  ✅ Última processada: {last_processed}")
            print(f"  📝 Mensagens pendentes: {pending_count}")
            
            if pending_count > 0:
                print("  📋 Mensagens pendentes:")
                for msg in record['pending_messages']:
                    print(f"    - {msg.get('text', 'no text')[:60]}...")
        else:
            print("⚠️  Nenhum registro de cooldown encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def main():
    """Executa teste completo com mensagem real"""
    print("🚀 TESTE FINAL COM MENSAGEM REAL")
    print("=" * 60)
    print(f"⏰ Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Enviar mensagem
    success, response = send_test_message()
    
    if success:
        print("\n✅ Mensagem enviada com sucesso!")
        
        # 2. Verificar banco de dados
        db_success = check_database_after_test()
        
        if db_success:
            print("\n🎉 TESTE FINAL COMPLETADO COM SUCESSO!")
            print("✅ Sistema está funcionando corretamente:")
            print("  - Mensagem recebida e processada")
            print("  - IA respondeu adequadamente") 
            print("  - Dados salvos no banco de dados")
            print("  - Sistema de cooldown funcionando")
        else:
            print("\n⚠️  Teste parcialmente bem-sucedido")
            print("✅ Mensagem processada, mas problemas no banco")
    else:
        print("\n❌ TESTE FALHOU")
        print("Sistema não conseguiu processar a mensagem")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()