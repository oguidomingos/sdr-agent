# Design Document

## Overview

Esta migração visa transformar a aplicação SDR Agent de uma arquitetura tradicional para uma arquitetura cloud-native totalmente funcional no Vercel, utilizando Supabase como banco de dados PostgreSQL gerenciado. A migração será baseada na branch multi-tenancy e implementada em uma nova branch dedicada para testes.

## Architecture

### Current Architecture
- **Backend**: FastAPI com PostgreSQL (Neon)
- **Frontend**: React/Vite com TypeScript
- **Database**: PostgreSQL via Neon
- **Deployment**: Vercel (com problemas de CORS)

### Target Architecture
- **Backend**: FastAPI serverless functions no Vercel
- **Frontend**: React/Vite estático no Vercel
- **Database**: Supabase PostgreSQL
- **Cache/Sessions**: Upstash Redis (serverless Redis)
- **WhatsApp Integration**: Evolution API externa (https://evolutionapi.centralsupernova.com.br)
- **Authentication**: Supabase Auth (opcional) ou manter JWT atual
- **Storage**: Supabase Storage para arquivos
- **Real-time**: Supabase Realtime para mensagens
- **Development Tools**: Vercel MCP + Supabase MCP para automação

## Components and Interfaces

### 1. Database Migration (PostgreSQL → Supabase)

**Supabase Configuration:**
```typescript
// supabase/config.ts
export const supabaseConfig = {
  url: process.env.SUPABASE_URL,
  anonKey: process.env.SUPABASE_ANON_KEY,
  serviceKey: process.env.SUPABASE_SERVICE_ROLE_KEY
}
```

### 2. Redis Migration (Current Redis → Upstash Redis)

**Upstash Redis Configuration:**
```python
# src/core/upstash_redis.py
import redis
import os

def get_redis_client():
    return redis.from_url(
        os.environ.get("UPSTASH_REDIS_REST_URL"),
        password=os.environ.get("UPSTASH_REDIS_REST_TOKEN"),
        decode_responses=True
    )
```

**Session Management with Upstash:**
```python
# src/core/session.py
from src.core.upstash_redis import get_redis_client

class SessionManager:
    def __init__(self):
        self.redis = get_redis_client()
    
    async def store_session(self, user_id: str, client_id: str, data: dict):
        key = f"session:{client_id}:{user_id}"
        await self.redis.setex(key, 3600, json.dumps(data))
    
    async def get_session(self, user_id: str, client_id: str):
        key = f"session:{client_id}:{user_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
```

### 3. Evolution API Integration (External Service)

**Evolution API Configuration:**
```python
# src/core/evolution_external.py
import httpx
import os

class EvolutionAPIClient:
    def __init__(self):
        self.base_url = "https://evolutionapi.centralsupernova.com.br"
        self.api_key = "509dbd54-c20c-4a5b-b889-a0494a861f5a"
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
    
    async def send_message(self, instance: str, number: str, message: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/message/sendText/{instance}",
                headers=self.headers,
                json={
                    "number": number,
                    "text": message
                }
            )
            return response.json()
    
    async def create_instance(self, instance_name: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/instance/create",
                headers=self.headers,
                json={
                    "instanceName": instance_name,
                    "token": instance_name,
                    "qrcode": True
                }
            )
            return response.json()
```

### 4. MCP Integration for Development

**Vercel MCP Configuration:**
```json
{
  "mcpServers": {
    "vercel": {
      "command": "uvx",
      "args": ["mcp-server-vercel@latest"],
      "env": {
        "VERCEL_TOKEN": "your-vercel-token"
      }
    },
    "supabase": {
      "command": "uvx", 
      "args": ["mcp-server-supabase@latest"],
      "env": {
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "your-service-role-key"
      }
    }
  }
}
```

**Upstash Redis Configuration:**
```python
# src/core/upstash_redis.py
import redis
import os

def get_redis_client():
    return redis.from_url(
        os.environ.get("UPSTASH_REDIS_REST_URL"),
        password=os.environ.get("UPSTASH_REDIS_REST_TOKEN"),
        decode_responses=True
    )
```

**Session Management with Upstash:**
```python
# src/core/session.py
from src.core.upstash_redis import get_redis_client

class SessionManager:
    def __init__(self):
        self.redis = get_redis_client()
    
    async def store_session(self, user_id: str, client_id: str, data: dict):
        key = f"session:{client_id}:{user_id}"
        await self.redis.setex(key, 3600, json.dumps(data))
    
    async def get_session(self, user_id: str, client_id: str):
        key = f"session:{client_id}:{user_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
```

**Database Schema Migration:**
- Migrar todas as tabelas existentes (users, clients, messages, playbooks, agent_configs)
- Configurar Row Level Security (RLS) para multi-tenancy
- Implementar políticas de acesso baseadas em client_id
- Configurar índices otimizados para performance

### 2. Backend Refactoring

**Serverless Functions Structure:**
```
api/
├── auth/
│   ├── login.py
│   ├── register.py
│   └── refresh.py
├── clients/
│   ├── [id].py
│   └── index.py
├── messages/
│   ├── [id].py
│   └── index.py
├── webhook/
│   └── whatsapp.py
└── health.py
```

**Database Connection:**
```python
# src/core/supabase_db.py
from supabase import create_client, Client
import os

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)
```

### 3. CORS Resolution

**Vercel Configuration Update:**
```json
{
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.9"
    }
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "https://your-domain.vercel.app"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        },
        {
          "key": "Access-Control-Allow-Headers",
          "value": "Content-Type, Authorization"
        }
      ]
    }
  ]
}
```

### 4. Environment Variables Migration

**Environment Variables Migration:**
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Upstash Redis Configuration
UPSTASH_REDIS_REST_URL=https://your-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-redis-token

# Evolution API Configuration (External)
EVOLUTION_API_URL=https://evolutionapi.centralsupernova.com.br
EVOLUTION_API_KEY=509dbd54-c20c-4a5b-b889-a0494a861f5a

# Remove old database/redis config
# DATABASE_URL (replaced by Supabase)
# POSTGRES_* variables (replaced by Supabase)
# REDIS_HOST, REDIS_PORT, REDIS_PASSWORD (replaced by Upstash)
```

### 5. Frontend Updates

**API Client Update:**
```typescript
// src/lib/api.ts
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-app.vercel.app/api'
  : 'http://localhost:3000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## Data Models

### Supabase Schema with RLS

**Users Table:**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  status user_status DEFAULT 'active',
  plan VARCHAR(50) DEFAULT 'free',
  max_clients INTEGER DEFAULT 10,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
```

**Clients Table with RLS:**
```sql
CREATE TABLE clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  domain VARCHAR(255) UNIQUE,
  status client_status DEFAULT 'trial',
  -- ... other fields
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own clients" ON clients 
  FOR ALL USING (owner_id = auth.uid());
```

## Error Handling

### 1. Database Connection Errors
```python
async def handle_supabase_error(error: Exception):
    if "connection" in str(error).lower():
        return {"error": "Database connection failed", "retry": True}
    elif "unauthorized" in str(error).lower():
        return {"error": "Authentication failed", "retry": False}
    else:
        return {"error": "Database operation failed", "retry": True}
```

### 2. CORS Error Prevention
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Serverless Function Timeouts
```python
import asyncio
from functools import wraps

def timeout_handler(seconds=25):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                return {"error": "Request timeout", "status": 408}
        return wrapper
    return decorator
```

## Testing Strategy

### 1. Migration Testing
- **Database Migration Test**: Verificar se todos os dados são migrados corretamente
- **Schema Validation**: Confirmar que todas as tabelas e índices foram criados
- **RLS Testing**: Testar políticas de segurança de linha

### 2. API Testing
- **Endpoint Testing**: Testar todos os endpoints após migração
- **Authentication Testing**: Verificar login/logout funcionando
- **CORS Testing**: Confirmar que não há mais erros de CORS

### 3. Integration Testing
- **WhatsApp Integration**: Testar webhook e envio de mensagens
- **Frontend-Backend**: Testar comunicação completa
- **Multi-tenant**: Verificar isolamento entre clientes

### 4. Performance Testing
- **Cold Start**: Medir tempo de inicialização das funções serverless
- **Database Performance**: Comparar performance com setup anterior
- **Load Testing**: Testar sob carga simulada

## Migration Steps

### Phase 1: Environment Setup
1. Criar projeto no Supabase
2. Criar database no Upstash Redis
3. Configurar MCPs do Vercel e Supabase
4. Configurar variáveis de ambiente no Vercel
5. Criar nova branch baseada em multi-tenancy
6. Testar conexão com Evolution API externa

### Phase 2: Database & Cache Migration
1. Exportar schema atual do PostgreSQL
2. Criar tabelas no Supabase
3. Configurar RLS policies
4. Migrar dados existentes
5. Configurar Upstash Redis para sessões e cache

### Phase 3: Backend Refactoring
1. Refatorar conexões de banco para Supabase
2. Adaptar código para funções serverless
3. Implementar tratamento de erros específico

### Phase 4: Frontend Updates
1. Atualizar URLs da API
2. Testar integração com novo backend
3. Implementar tratamento de erros

### Phase 5: Testing & Deployment
1. Testes locais completos
2. Deploy em ambiente de staging
3. Testes de integração
4. Deploy em produção

## Security Considerations

### 1. Supabase Security
- Configurar RLS adequadamente
- Usar service role key apenas no backend
- Implementar políticas de acesso granulares

### 2. API Security
- Manter JWT authentication
- Implementar rate limiting
- Validar todas as entradas

### 3. CORS Security
- Configurar origins específicos
- Evitar wildcards em produção
- Implementar CSP headers