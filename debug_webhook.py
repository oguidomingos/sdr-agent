#!/usr/bin/env python3
"""
Debug webhook para testar processamento AI local
"""
import requests
import json

# Dados do webhook real
webhook_data = {
    "event": "messages.upsert",
    "instance": "sdr_3f30b5be", 
    "data": {
        "key": {
            "remoteJid": "5561936180578@s.whatsapp.net",
            "fromMe": False,
            "id": "3A5F2EC415239B0A142C"
        },
        "message": {
            "conversation": "oi"
        }
    }
}

# Configuração do cliente (da nossa base)
client_config = {
    "id": "3f30b5be-2e5d-4bf8-8c76-24f39d1d548e",
    "name": "Teste Webhook Melhorado",
    "evolution_api_key": "509dbd54-c20c-4a5b-b889-a0494a861f5a", 
    "gemini_api_key": "AIzaSyASsQw-arw3Mqp7q01qy37Wxkrj-Lo0oHk",
    "agent_persona": "Sou um assistente para testar as melhorias no webhook do Evolution API.",
    "evolution_instance": "sdr_3f30b5be"
}

print("🔍 Testando processamento AI...")

# Testar Gemini AI
try:
    import google.generativeai as genai
    
    genai.configure(api_key=client_config['gemini_api_key'])
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    system_prompt = f"""
Você é um assistente de vendas inteligente. 

PERSONA DO AGENTE:
{client_config['agent_persona']}

INSTRUÇÕES:
- Use a persona fornecida para responder
- Seja natural e conversacional
- Faça perguntas para qualificar o lead
- Mantenha respostas concisas (máximo 200 caracteres)
- Use o método SPIN Selling quando apropriado

MENSAGEM DO USUÁRIO: oi

Responda de forma profissional e útil:
"""
    
    response = model.generate_content(system_prompt)
    
    if response and response.text:
        ai_response = response.text.strip()
        print(f"✅ AI Response: {ai_response}")
        
        # Testar envio via Evolution API
        evolution_url = "https://evolutionapi.centralsupernova.com.br"
        url = f"{evolution_url}/message/sendText/{client_config['evolution_instance']}"
        
        payload = {
            "number": "5561936180578",
            "text": ai_response
        }
        
        headers = {
            "Content-Type": "application/json",
            "apikey": client_config['evolution_api_key']
        }
        
        print("🔍 Enviando mensagem via Evolution API...")
        evolution_response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if evolution_response.status_code == 201:
            print("✅ Mensagem enviada com sucesso!")
            print(f"Response: {evolution_response.json()}")
        else:
            print(f"❌ Erro ao enviar: {evolution_response.status_code} - {evolution_response.text}")
            
    else:
        print("❌ AI não gerou resposta")
        
except Exception as e:
    print(f"❌ Erro no processamento: {e}")