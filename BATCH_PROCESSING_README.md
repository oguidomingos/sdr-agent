# 🚀 Sistema de Processing em Lotes - Melhorias Implementadas

## 📋 Resumo das Melhorias

### 1. ✅ Limite de Caracteres Aumentado
- **Antes**: Mensagens limitadas a 300 caracteres
- **Depois**: Mensagens limitadas a 2000 caracteres
- **Arquivo modificado**: `src/core/whatsapp.py:69`

### 2. ✅ Sistema de Batch Processing
Implementado um sistema inteligente que agrupa mensagens do usuário em janelas de tempo, evitando múltiplas requisições desnecessárias para a API do Gemini.

#### Características:
- **Janela de tempo**: 3 minutos (180 segundos)
- **Configurável**: Entre 2-5 minutos
- **Inteligente**: Cancela timers anteriores quando nova mensagem chega
- **Robusto**: Sistema de fallback caso o batch falhe

#### Arquivos Criados/Modificados:
- **Novo**: `src/core/batch_processor.py` - Sistema de batch processing
- **Modificado**: `src/api/routes.py` - Integração com o webhook

## 🔄 Como Funciona o Batch Processing

### Fluxo Normal:
1. **Primeira mensagem**: Usuário envia primeira mensagem → Bot responde imediatamente com saudação
2. **Mensagens subsequentes**: 
   - Mensagem é adicionada ao lote ativo
   - Timer de 3 minutos é iniciado/reiniciado
   - Se usuário enviar mais mensagens na janela, são agregadas ao mesmo lote
   - Após 3 minutos de silêncio, o lote é processado como uma única requisição

### Exemplo Prático:
```
13:00:00 - Usuário: "Oi"
13:00:01 - Bot: "Olá! Como posso ajudar?" (resposta imediata - primeira mensagem)

13:01:00 - Usuário: "Preciso de ajuda"
13:01:05 - Usuário: "Com consulta médica"  
13:01:10 - Usuário: "Para minha mãe"
13:01:15 - Usuário: "Ela tem 65 anos"

13:04:15 - Bot processa TODAS as 4 mensagens juntas:
           "Preciso de ajuda\nCom consulta médica\nPara minha mãe\nEla tem 65 anos"
13:04:20 - Bot: Resposta contextualizada considerando todas as informações
```

## 📊 Endpoints Adicionais

### Consultar Status de Lote Ativo
```http
GET /batch/{user_id}
```
**Resposta:**
```json
{
  "user_id": "5561999999999@s.whatsapp.net",
  "message_count": 3,
  "first_message_time": "2025-01-30T16:01:00.000Z",
  "last_message_time": "2025-01-30T16:01:15.000Z",
  "time_remaining": 180,
  "combined_content": "Preciso de ajuda\nCom consulta médica\nPara minha mãe"
}
```

### Forçar Processamento Imediato
```http
POST /batch/{user_id}/process
```
**Resposta:**
```json
{
  "status": "batch_processed",
  "user_id": "5561999999999@s.whatsapp.net"
}
```

## 🎯 Benefícios

### 1. **Economia de Requisições**
- **Antes**: 4 mensagens = 4 chamadas para Gemini
- **Depois**: 4 mensagens = 1 chamada para Gemini (economia de 75%)

### 2. **Melhor Contexto**
- Bot tem acesso a todas as mensagens da janela de tempo
- Respostas mais contextualmente ricas e precisas
- Evita respostas fragmentadas

### 3. **Experiência do Usuário**
- Usuário pode enviar pensamentos completos sem pressa
- Bot responde de forma mais natural e completa
- Mensagens maiores (até 2000 caracteres) são suportadas

### 4. **Eficiência**
- Reduz custos de API
- Melhora performance
- Sistema mais escalável

## ⚙️ Configurações

### Variáveis de Ambiente (Opcionais)
```env
# Janela de batch em segundos (padrão: 180)
BATCH_WINDOW_SECONDS=180

# Janela mínima (padrão: 120)
MIN_BATCH_WINDOW_SECONDS=120

# Janela máxima (padrão: 300)
MAX_BATCH_WINDOW_SECONDS=300
```

### Modificar em Código
```python
# Em src/api/routes.py linha 22
batch_processor = BatchProcessor(batch_window_seconds=240)  # 4 minutos
```

## 🧪 Como Testar

### 1. Teste de Primeira Mensagem
```bash
# Deve responder imediatamente
curl -X POST http://localhost:8000/webhook/whatsapp -d '{...}'
```

### 2. Teste de Batch
```bash
# Envie várias mensagens rapidamente
# Aguarde 3 minutos
# Verifique se bot responde uma única vez com contexto completo
```

### 3. Verificar Status de Lote
```bash
curl http://localhost:8000/batch/5561999999999@s.whatsapp.net
```

### 4. Forçar Processamento
```bash
curl -X POST http://localhost:8000/batch/5561999999999@s.whatsapp.net/process
```

## 🔍 Logs de Debug

O sistema adiciona logs detalhados para acompanhar o funcionamento:

```
📦 Mensagem adicionada ao lote do usuário 5561999999999@s.whatsapp.net. Total no lote: 3 mensagens
🔄 Processando lote para 5561999999999@s.whatsapp.net com 3 mensagens
📝 Conteúdo combinado: Preciso de ajuda\nCom consulta médica\nPara minha mãe...
🤖 Enviando mensagem combinada para o Gemini...
📤 Enviando resposta do lote...
✅ Lote processado com sucesso para 5561999999999@s.whatsapp.net
```

## 🔧 Manutenção

### Limpeza Automática
O sistema possui limpeza automática de lotes expirados:
```python
await batch_processor.cleanup_expired_batches()
```

### Monitoramento
- Logs detalhados em tempo real
- Endpoints de status para debugging
- Sistema de fallback robusto

## 🚨 Possíveis Melhorias Futuras

1. **Configuração por Cliente**: Diferentes janelas de tempo por cliente
2. **Inteligência Adaptativa**: Ajustar janela baseado no padrão do usuário
3. **Métricas**: Dashboard com estatísticas de economia de requisições
4. **Priorização**: Processar lotes VIP mais rapidamente