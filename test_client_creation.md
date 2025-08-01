# Teste de Criação de Cliente com WhatsApp

## Status Atual
- ✅ Limite de clientes aumentado de 3 para 10
- ✅ Campo `whatsapp_number` adicionado ao banco de dados
- ✅ Validação frontend implementada
- ✅ Componente WhatsAppConnection criado

## Para Testar

### 1. Criação de Novo Cliente
1. Acesse o frontend em http://localhost:3000
2. Faça login com suas credenciais
3. Clique em "Novo Cliente"
4. Preencha os campos obrigatórios:
   - **Nome**: Ex: "Teste WhatsApp"
   - **Domínio**: Ex: "teste-whatsapp.sdr-agent.com"
   - **Número do WhatsApp**: Ex: "+5511999999999" (OBRIGATÓRIO)
5. Configure as APIs (Evolution e Gemini)
6. Clique em "Criar Cliente"

### 2. Conexão WhatsApp
1. No card do cliente criado, clique no botão "WhatsApp"
2. Modal abrirá com duas opções:
   - **QR Code**: Clique em "Gerar QR Code" e escaneie
   - **Código de Pareamento**: Digite o código do WhatsApp

### 3. Verificação
- Badge no card deve mostrar status da conexão
- Status atualiza automaticamente a cada 5 segundos

## Clientes Existentes
Os clientes existentes não têm número WhatsApp configurado:
- wolf - WhatsApp: Not set
- jordan - WhatsApp: Not set  
- 3roi - WhatsApp: Not set

Para estes clientes, você pode:
1. Editá-los para adicionar o número WhatsApp
2. Ou criar novos clientes com o campo obrigatório

## Próximos Passos
1. Teste a criação de um novo cliente
2. Verifique se o QR Code é gerado corretamente
3. Teste a conexão via código de pareamento
4. Confirme que o status atualiza em tempo real