# Design Document

## Overview

O problema de CORS em produção na Vercel está ocorrendo porque há uma incompatibilidade entre as configurações de CORS no `vercel.json` e no código FastAPI, além de problemas específicos com o tratamento de preflight requests (OPTIONS) em ambiente serverless.

A análise do erro mostra que requisições estão sendo feitas entre diferentes deployments da Vercel (URLs diferentes), mas o preflight request não está retornando os headers CORS necessários, indicando que o middleware CORS não está sendo aplicado corretamente ou que há conflitos de configuração.

## Architecture

### Problema Identificado

1. **Conflito de Configuração**: O `vercel.json` define headers CORS, mas o FastAPI também tem seu próprio middleware CORS
2. **Preflight Handling**: O handler OPTIONS personalizado pode estar conflitando com o middleware CORSMiddleware
3. **Serverless Context**: Em ambiente serverless, o middleware pode não estar sendo inicializado corretamente
4. **URL Mismatch**: Diferentes deployments da Vercel têm URLs diferentes, causando problemas de origem

### Solução Proposta

1. **Unificar Configuração CORS**: Remover duplicação entre vercel.json e FastAPI
2. **Simplificar Middleware**: Usar apenas uma abordagem para CORS
3. **Handler Dedicado**: Criar um handler específico para preflight requests
4. **Configuração Dinâmica**: Detectar automaticamente origens da Vercel

## Components and Interfaces

### 1. CORS Configuration Module (`src/core/cors_config.py`)

**Responsabilidades:**
- Detectar ambiente (desenvolvimento vs produção)
- Configurar origens permitidas dinamicamente
- Fornecer configuração unificada de CORS

**Interface:**
```python
def get_vercel_origins() -> List[str]
def get_cors_config_for_vercel() -> dict
def is_vercel_environment() -> bool
```

### 2. FastAPI CORS Setup (`api/main.py`)

**Responsabilidades:**
- Aplicar middleware CORS corretamente
- Tratar preflight requests
- Garantir compatibilidade com Vercel

**Modificações:**
- Remover handler OPTIONS personalizado
- Configurar middleware CORS adequadamente
- Adicionar headers de resposta dinâmicos

### 3. Vercel Configuration (`vercel.json`)

**Responsabilidades:**
- Configurar headers HTTP básicos
- Remover configurações CORS conflitantes
- Manter apenas headers de segurança

**Modificações:**
- Remover headers CORS do vercel.json
- Deixar CORS ser tratado apenas pelo FastAPI
- Manter headers de segurança

### 4. Production CORS Handler

**Responsabilidades:**
- Detectar origens da Vercel automaticamente
- Tratar casos especiais de produção
- Garantir compatibilidade entre deployments

## Data Models

### CORS Configuration Model

```python
@dataclass
class CORSConfig:
    allow_origins: List[str]
    allow_credentials: bool
    allow_methods: List[str]
    allow_headers: List[str]
    max_age: int
    expose_headers: List[str]
```

### Vercel Environment Model

```python
@dataclass
class VercelEnvironment:
    deployment_url: str
    environment: str  # production, preview, development
    region: str
    is_vercel: bool
```

## Error Handling

### CORS Error Scenarios

1. **Preflight Failure**: Quando OPTIONS request falha
   - **Handling**: Retornar headers CORS apropriados
   - **Fallback**: Handler dedicado para OPTIONS

2. **Origin Mismatch**: Quando origem não é permitida
   - **Handling**: Detectar origens da Vercel dinamicamente
   - **Fallback**: Permitir todas as origens em produção

3. **Header Missing**: Quando headers CORS não são enviados
   - **Handling**: Garantir que middleware seja aplicado
   - **Fallback**: Adicionar headers manualmente na resposta

4. **Method Not Allowed**: Quando método HTTP não é permitido
   - **Handling**: Incluir todos os métodos necessários
   - **Fallback**: Permitir todos os métodos em produção

### Error Response Format

```python
{
    "error": "CORS_ERROR",
    "message": "Cross-origin request blocked",
    "details": {
        "origin": "https://example.com",
        "method": "POST",
        "headers": ["Content-Type", "Authorization"]
    },
    "solution": "Configure CORS properly"
}
```

## Testing Strategy

### Unit Tests

1. **CORS Configuration Tests**
   - Testar detecção de ambiente
   - Testar geração de origens permitidas
   - Testar configuração dinâmica

2. **Middleware Tests**
   - Testar aplicação de headers CORS
   - Testar tratamento de preflight requests
   - Testar diferentes origens

### Integration Tests

1. **API Endpoint Tests**
   - Testar requisições com diferentes origens
   - Testar preflight requests
   - Testar métodos HTTP diferentes

2. **Production Environment Tests**
   - Testar com URLs da Vercel
   - Testar entre diferentes deployments
   - Testar com frontend real

### End-to-End Tests

1. **Browser Tests**
   - Testar requisições do frontend
   - Testar diferentes navegadores
   - Testar cenários de erro

2. **Deployment Tests**
   - Testar após deploy na Vercel
   - Testar com diferentes configurações
   - Testar rollback de configurações

## Implementation Approach

### Phase 1: Cleanup and Simplification
- Remover configurações CORS conflitantes
- Simplificar middleware CORS
- Remover handler OPTIONS personalizado

### Phase 2: Dynamic Configuration
- Implementar detecção de ambiente Vercel
- Configurar origens dinamicamente
- Adicionar logging para debug

### Phase 3: Production Optimization
- Otimizar para ambiente serverless
- Adicionar cache de configuração
- Implementar fallbacks robustos

### Phase 4: Testing and Validation
- Testar em produção
- Validar com diferentes cenários
- Monitorar erros de CORS

## Security Considerations

1. **Origin Validation**: Mesmo permitindo múltiplas origens, validar que são da Vercel
2. **Credential Handling**: Configurar allow_credentials adequadamente
3. **Header Exposure**: Expor apenas headers necessários
4. **Method Restriction**: Permitir apenas métodos HTTP necessários

## Performance Considerations

1. **Middleware Order**: Aplicar CORS middleware primeiro
2. **Caching**: Cache configuração CORS para evitar recálculos
3. **Preflight Caching**: Configurar max_age adequadamente
4. **Header Size**: Minimizar tamanho dos headers CORS