# 🚀 Guia Completo - Evolution API + SDR Agent Multi-Client

## ✅ Configuração Completa Realizada

### 📋 O que foi configurado:

1. **Evolution API clonada** em `/Users/oguidomingos/sdr-agent/evolution-api/`  
2. **Arquivo .env da Evolution API** criado com configurações otimizadas
3. **API Key gerada**: `B6D711FCDE4D4FD5936544120E713976`
4. **SDR Agent atualizado** com as configurações da Evolution API

---

## 🏃‍♂️ Como Iniciar Tudo

### **Passo 1: Iniciar o Docker Desktop**
```bash
# Abra o Docker Desktop no seu Mac
# Aguarde até que apareça "Docker Desktop is running" 
```

### **Passo 2: Iniciar a Evolution API**
```bash
# Navegue até o diretório da Evolution API
cd /Users/oguidomingos/sdr-agent/evolution-api

# Inicie os serviços (PostgreSQL, Redis, Evolution API)
docker-compose up -d

# Verifique se está rodando
docker-compose ps
```

**Resultado esperado:**
```
      Name                     Command               State           Ports         
---------------------------------------------------------------------------------
evolution_api      docker-entrypoint.sh node ...   Up      0.0.0.0:8080->8080/tcp
postgres           docker-entrypoint.sh postgres   Up      0.0.0.0:5432->5432/tcp  
redis              docker-entrypoint.sh redis-s... Up      0.0.0.0:6379->6379/tcp
```

### **Passo 3: Verificar a Evolution API**
```bash
# Teste se a API está respondendo
curl http://localhost:8080

# Ou abra no navegador:
# http://localhost:8080
```

### **Passo 4: Iniciar o SDR Agent**
```bash
# Volte para o diretório do SDR Agent
cd /Users/oguidomingos/sdr-agent

# Inicie apenas o SDR Agent (a Evolution API já está rodando)
docker-compose up app -d
```

---

## 🔑 Informações Importantes

### **Credenciais da Evolution API:**
- **URL**: `http://localhost:8888`
- **API Key**: `B6D711FCDE4D4FD5936544120E713976`
- **Instância Padrão**: `sdr-agent`

### **URLs de Acesso:**
- **Evolution API**: http://localhost:8888
- **SDR Agent API**: http://localhost:8000
- **SDR Agent Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### **Portas Utilizadas:**
- **Evolution API**: 8888
- **Evolution Redis**: 6365
- **Evolution PostgreSQL**: 5434
- **SDR Agent**: 8000
- **SDR Agent Redis**: 6380
- **SDR Agent PostgreSQL**: 5433

---

## 📱 Configurando WhatsApp

### **1. Criar uma Instância no Evolution API**
```bash
curl -X POST http://localhost:8888/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: B6D711FCDE4D4FD5936544120E713976" \
  -d '{
    "instanceName": "sdr-agent",
    "qrcode": true,
    "webhook": "http://localhost:8000/webhook/whatsapp"
  }'
```

### **2. Obter o QR Code**
```bash
curl -X GET http://localhost:8888/instance/connect/sdr-agent \
  -H "apikey: B6D711FCDE4D4FD5936544120E713976"
```

### **3. Escanear com WhatsApp Business**
1. Abra o **WhatsApp Business** no seu celular
2. Vá em **Mais opções** > **Dispositivos conectados**
3. Toque em **Conectar um dispositivo**
4. Escaneie o QR Code retornado pela API

---

## 🔧 Comandos Úteis

### **Verificar Status dos Serviços:**
```bash
# Evolution API
cd /Users/oguidomingos/sdr-agent/evolution-api
docker-compose ps

# SDR Agent  
cd /Users/oguidomingos/sdr-agent
docker-compose ps
```

### **Ver Logs em Tempo Real:**
```bash
# Evolution API
cd /Users/oguidomingos/sdr-agent/evolution-api
docker-compose logs -f api

# SDR Agent
cd /Users/oguidomingos/sdr-agent  
docker-compose logs -f app
```

### **Parar os Serviços:**
```bash
# Parar Evolution API
cd /Users/oguidomingos/sdr-agent/evolution-api
docker-compose down

# Parar SDR Agent
cd /Users/oguidomingos/sdr-agent
docker-compose down
```

### **Reiniciar Tudo:**
```bash
# Evolution API
cd /Users/oguidomingos/sdr-agent/evolution-api
docker-compose restart

# SDR Agent
cd /Users/oguidomingos/sdr-agent
docker-compose restart
```

---

## 🧪 Testando a Integração

### **1. Verificar se a Evolution API está funcionando:**
```bash
curl -X GET http://localhost:8888/instance/fetchInstances \
  -H "apikey: B6D711FCDE4D4FD5936544120E713976"
```

### **2. Verificar se o SDR Agent está funcionando:**
```bash
curl http://localhost:8000/health
```

### **3. Testar envio de mensagem (após conectar WhatsApp):**
```bash
curl -X POST http://localhost:8888/message/sendText/sdr-agent \
  -H "Content-Type: application/json" \
  -H "apikey: B6D711FCDE4D4FD5936544120E713976" \
  -d '{
    "number": "5511999999999",
    "options": {
      "delay": 1200
    },
    "textMessage": {
      "text": "Olá! Sou o assistente SDR. Como posso ajudá-lo?"
    }
  }'
```

---

## 🚨 Troubleshooting

### **Problema: Docker não está rodando**
```bash
# Solução: Abra o Docker Desktop e aguarde inicializar
open -a Docker
```

### **Problema: Porta 8888 já está em uso**
```bash
# Verifique qual processo está usando a porta
lsof -i :8888

# Mate o processo se necessário
kill -9 <PID>
```

### **Problema: Evolution API não conecta ao banco**
```bash
# Reinicie apenas o banco de dados
cd /Users/oguidomingos/sdr-agent/evolution-api
docker-compose restart postgres
docker-compose restart api
```

### **Problema: SDR Agent não conecta à Evolution API**
```bash
# Verifique se a Evolution API está respondendo
curl http://localhost:8888

# Verifique os logs do SDR Agent
cd /Users/oguidomingos/sdr-agent
docker-compose logs app
```

---

## 🎉 Próximos Passos

1. **Inicie o Docker Desktop**
2. **Execute os comandos dos Passos 2-4** 
3. **Configure o WhatsApp** seguindo a seção "Configurando WhatsApp"
4. **Teste a integração** com os comandos da seção "Testando a Integração"

Tudo está configurado e pronto para uso! 🚀