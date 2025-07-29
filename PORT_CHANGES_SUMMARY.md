# 🔄 Configuração de Portas Personalizadas - Resumo das Mudanças

## ✅ **Portas Configuradas**

### **Evolution API:**
- **Porta Externa**: `8888` (em vez de 8080)
- **Porta Interna**: `8080` (no container)
- **URL de Acesso**: `http://localhost:8888`

### **Redis da Evolution API:**
- **Porta Externa**: `6365` (em vez de 6379)
- **Porta Interna**: `6379` (no container)
- **Container**: `redis_evolution`

### **SDR Agent:**
- **Porta API**: `8000` (mantida)
- **Redis Porta**: `6380` (em vez de 6379)
- **Container Redis**: `redis_sdr`

### **PostgreSQL Evolution API:**
- **Porta Externa**: `5434` (em vez de 5432)
- **Container**: `postgres_evolution`

### **PostgreSQL SDR Agent:**
- **Porta Externa**: `5433` (em vez de 5432)
- **Container**: `postgres_sdr`

---

## 📝 **Arquivos Modificados**

### **1. Evolution API - docker-compose.yaml**
```yaml
# Mudança na porta da API
ports:
  - 8888:8080  # Era 8080:8080

# Mudança no Redis
container_name: redis_evolution  # Era redis
ports:
  - 6365:6379  # Era 6379:6379
```

### **2. Evolution API - .env**
```bash
# URL atualizada
SERVER_URL=http://localhost:8888  # Era http://localhost:8080

# Redis URI atualizada
CACHE_REDIS_URI=redis://redis_evolution:6379/6  # Era redis://redis:6379/6
```

### **3. SDR Agent - docker-compose.yml**
```yaml
# Redis com novo container name e porta
redis:
  container_name: redis_sdr  # Era sem nome específico
  ports:
    - "6380:6379"  # Era "6379:6379"

# PostgreSQL com nova porta
postgres:
  container_name: postgres_sdr  # Era sem nome específico
  ports:
    - "5433:5432"  # Era "5432:5432"
```

### **4. SDR Agent - .env**
```bash
# Evolution API URL atualizada
EVOLUTION_API_URL=http://localhost:8888  # Era http://localhost:8080

# Database host atualizado
POSTGRES_HOST=postgres_sdr  # Era postgres
DATABASE_URL=postgresql+asyncpg://sdr_user:sdr_password@postgres_sdr:5432/sdr_agent

# Redis host atualizado
REDIS_HOST=redis_sdr  # Era redis
```

### **5. EVOLUTION_SETUP_GUIDE.md**
- Todas as URLs e comandos curl atualizados para usar porta 8888
- Documentação das novas portas adicionada
- Comandos de troubleshooting atualizados

---

## 🚀 **Como Usar as Novas Portas**

### **Iniciar Evolution API:**
```bash
cd /Users/oguidomingos/sdr-agent/evolution-api
docker-compose up -d

# Testar acesso
curl http://localhost:8888
```

### **Iniciar SDR Agent:**
```bash
cd /Users/oguidomingos/sdr-agent
docker-compose up -d

# Testar acesso
curl http://localhost:8000/health
```

### **Criar Instância WhatsApp:**
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

---

## 🔍 **Verificar Portas em Uso**

```bash
# Verificar todas as portas configuradas
netstat -tulnp | grep -E "(8888|8000|6365|6380|5433|5434)"

# Ou usando lsof
lsof -i :8888  # Evolution API
lsof -i :8000  # SDR Agent
lsof -i :6365  # Redis Evolution
lsof -i :6380  # Redis SDR Agent
lsof -i :5433  # PostgreSQL SDR Agent
lsof -i :5434  # PostgreSQL Evolution
```

---

## 🎯 **Benefícios da Nova Configuração**

### **1. Evita Conflitos de Porta**
- Não há mais conflito com serviços que usam porta 8080
- Redis isolado por projeto

### **2. Isolamento de Serviços**
- Cada projeto tem seu próprio Redis
- Containers nomeados para facilitar identificação

### **3. Facilita Desenvolvimento**
- Possível rodar múltiplos projetos simultaneamente
- Debugging mais fácil com containers nomeados

### **4. Flexibilidade**
- Fácil de alterar portas se necessário
- Configuração centralizada nos arquivos .env

---

## ⚠️ **Coisas Importantes**

1. **Sempre use a porta 8888** para acessar a Evolution API
2. **O SDR Agent continua na porta 8000**
3. **Redis são isolados** - cada projeto tem o seu
4. **PostgreSQL são isolados** - Evolution na 5434, SDR Agent na 5433
5. **Todos os comandos curl** foram atualizados para usar 8888

---

## 🔄 **Se Precisar Voltar às Portas Originais**

Para reverter às portas padrão (8080, 6379), basta:

1. Alterar `8888:8080` para `8080:8080` nos docker-compose
2. Alterar `6365:6379` para `6379:6379` nos docker-compose  
3. Atualizar URLs nos arquivos .env
4. Reiniciar os containers

Tudo está configurado e pronto para uso com as novas portas! 🚀