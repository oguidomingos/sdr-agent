# 📋 Configuração Atual do Webhook

## 🔗 URLs Configuradas

### 1. Evolution API (Painel Manager)
```
URL: http://172.18.0.5:8000/webhook/whatsapp/1d583bf9-82c8-4d2a-a0d0-63e1cff5ee4b
Status: ✅ ATIVO
Eventos: MESSAGES_UPSERT, CONNECTION_UPDATE, QRCODE_UPDATED
```

### 2. Banco de Dados (Cliente)
```
Cliente: jdn
Instance: whatsapp_5561999449983_ade7e601_jdn
Webhook URL: http://172.18.0.5:8000/webhook/whatsapp/1d583bf9-82c8-4d2a-a0d0-63e1cff5ee4b
```

### 3. Configuração Base (.env)
```
WEBHOOK_BASE_URL=http://172.18.0.5:8000
```

## 🌐 Configuração de Rede

### Problema Original:
- **Evolution API**: Rede `evolution-net` (172.18.0.x)
- **SDR Agent**: Rede `sdr-agent_default` (172.19.0.x)
- **Resultado**: Sem comunicação entre containers

### Solução Aplicada:
- **SDR Agent conectado** à rede `evolution-net`
- **IP na rede evolution-net**: `172.18.0.5`
- **Webhook atualizado** para usar IP interno

## 📡 Fluxo de Comunicação

```
WhatsApp (+5561999449983)
    ↓ (mensagem)
Evolution API (localhost:8888)
    ↓ (webhook HTTP POST)
SDR Agent (172.18.0.5:8000/webhook/whatsapp/{client_id})
    ↓ (processamento)
Batch System (180s window)
    ↓ (IA)
Gemini AI
    ↓ (resposta)
Evolution API → WhatsApp
```

## ✅ Status de Funcionamento

### Testes Realizados:
1. **Conectividade**: ✅ Evolution API → SDR Agent
2. **Webhook Processing**: ✅ Mensagens sendo recebidas
3. **Batch System**: ✅ Agrupamento em 180s
4. **Database**: ✅ Sessões sendo salvas
5. **Logs**: ✅ Processamento visível

### Resposta do Webhook:
```json
{
  "status": "message_batched",
  "client_id": "1d583bf9-82c8-4d2a-a0d0-63e1cff5ee4b",
  "batch_info": {
    "message_count": 1,
    "window_seconds": 180
  }
}
```

## 🔧 Para Novos Clientes

### Configuração Automática:
- **Base URL**: `http://172.18.0.5:8000`
- **Formato**: `/webhook/whatsapp/{client_id}`
- **Rede**: Aplicação já conectada à `evolution-net`

### Exemplo para Novo Cliente:
```
Cliente ID: abc123-def456-ghi789
Webhook: http://172.18.0.5:8000/webhook/whatsapp/abc123-def456-ghi789
```

## 🎯 Resumo Final

**O webhook está configurado em:**
```
http://172.18.0.5:8000/webhook/whatsapp/1d583bf9-82c8-4d2a-a0d0-63e1cff5ee4b
```

**Onde:**
- `172.18.0.5` = IP do SDR Agent na rede evolution-net
- `8000` = Porta da aplicação SDR Agent
- `/webhook/whatsapp/` = Rota base do webhook
- `1d583bf9-82c8-4d2a-a0d0-63e1cff5ee4b` = ID único do cliente

**Status: 🟢 TOTALMENTE FUNCIONAL**