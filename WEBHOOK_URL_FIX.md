# Correção da URL do Webhook

## Problema Identificado

Você observou que no painel da Evolution API, a URL do webhook estava configurada como:
```
http://host.docker.internal:8000/webhook/whatsapp/temp
```

## Análise do Problema

O problema ocorria porque:

1. **Durante a criação do cliente**: O sistema usa `client_id="temp"` temporariamente
2. **Webhook configurado**: A Evolution API recebe a URL com `/temp`
3. **Após criação**: O código tentava atualizar a URL no banco, mas não na Evolution API

## Correções Implementadas

### 1. Atualização Automática do Webhook
- **Arquivo**: `src/api/auth_routes.py`
- **Mudança**: Após criar o cliente, o sistema agora:
  - Atualiza a URL no banco de dados
  - **NOVO**: Atualiza também na Evolution API automaticamente

### 2. Método de Atualização de Webhook
- **Arquivo**: `src/core/evolution_integration.py`
- **Novo método**: `update_webhook_url()`
- **Função**: Reconfigura o webhook na Evolution API com a URL correta

### 3. Script de Correção
- **Arquivo**: `scripts/fix_webhook_urls.py`
- **Função**: Corrige clientes existentes que ficaram com `/temp`

## URL Correta do Webhook

### Formato Esperado:
```
http://host.docker.internal:8000/webhook/whatsapp/{client_id}
```

### Exemplo para um cliente real:
```
http://host.docker.internal:8000/webhook/whatsapp/abc123-def456-ghi789
```

## Configuração Atual

### Variáveis de Ambiente (.env):
```bash
WEBHOOK_BASE_URL=http://host.docker.internal:8000
```

### Rota da Aplicação:
```python
@router.post("/whatsapp/{client_id}")
async def handle_client_webhook(client_id: str, ...)
```

## Verificação

### 1. Para Novos Clientes:
- Ao criar um cliente, a URL será automaticamente corrigida
- O webhook na Evolution API será reconfigurado com a URL correta

### 2. Para Clientes Existentes:
- Execute o script de correção se necessário
- Ou reconfigure manualmente no painel da Evolution API

### 3. Teste da Rota:
```bash
# A rota deve existir (retorna Method Not Allowed para GET, mas aceita POST)
curl -X GET http://localhost:8000/webhook/whatsapp/test-client-id
# Resposta: {"detail":"Method Not Allowed"}
```

## Fluxo Correto Agora

1. **Usuário cria cliente** com número WhatsApp obrigatório
2. **Sistema cria instância** Evolution API temporariamente com `/temp`
3. **Cliente é salvo** no banco com ID real
4. **URL é atualizada** no banco: `/temp` → `/{client_id}`
5. **Webhook é reconfigurado** na Evolution API com URL correta
6. **Sistema está pronto** para receber webhooks no endpoint correto

## Resultado

✅ **Problema resolvido**: Novos clientes terão webhook configurado corretamente
✅ **Atualização automática**: Sistema corrige a URL após criação
✅ **Compatibilidade**: Funciona com a estrutura multi-tenant existente
✅ **Monitoramento**: Logs mostram se a atualização foi bem-sucedida

A URL `http://host.docker.internal:8000/webhook/whatsapp/temp` não deveria mais aparecer para novos clientes criados após esta correção.