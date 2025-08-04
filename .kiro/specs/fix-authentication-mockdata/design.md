# Design Document - Fix Authentication Mock Data

## Overview

Este documento descreve a solução para corrigir o problema de dados mockados na API de autenticação. O sistema atualmente retorna dados hardcoded ("Demo User", "user@example.com") mesmo após login bem-sucedido. A solução envolve identificar e corrigir implementações mockadas, garantir conexão adequada com Supabase, e fazer um novo deploy funcional.

## Architecture

### Current Problem Architecture
```
Frontend → API Login ✅ → JWT Token ✅
Frontend → API /auth/me ❌ → Mock Data (Demo User)
```

### Target Architecture
```
Frontend → API Login ✅ → JWT Token ✅
Frontend → API /auth/me ✅ → Supabase Query → Real User Data
```

### System Components

1. **Frontend (React/TypeScript)**
   - AuthContext: Gerencia estado de autenticação
   - AppLayout/AppSidebar: Exibe dados do usuário
   - API Client: Faz requisições para backend

2. **Backend API (FastAPI)**
   - Auth Router: Endpoints de autenticação
   - JWT Middleware: Validação de tokens
   - Supabase Integration: Conexão com banco

3. **Database (Supabase)**
   - Users Table: Dados reais dos usuários
   - Clients Table: Clientes por usuário
   - RLS Policies: Segurança por usuário

## Components and Interfaces

### 1. Authentication Flow

#### Current Implementation (Broken)
```python
# api/auth/router.py - PROBLEMA IDENTIFICADO
@router.get("/me", response_model=UserResponse)
async def get_current_user(token_data: dict = Depends(verify_token)):
    # ❌ IMPLEMENTAÇÃO MOCKADA - NÃO CONSULTA BANCO
    return UserResponse(
        id="user_5032",
        email="user@example.com",  # ❌ HARDCODED
        first_name="Demo",         # ❌ HARDCODED
        last_name="User",          # ❌ HARDCODED
        status="active",
        plan="trial"
    )
```

#### Target Implementation (Fixed)
```python
# api/auth/router.py - IMPLEMENTAÇÃO CORRETA
@router.get("/me", response_model=UserResponse)
async def get_current_user(token_data: dict = Depends(verify_token)):
    db = get_supabase_db()
    
    # ✅ CONSULTA BANCO REAL
    user = await db.get_user_by_id(token_data['user_id'])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # ✅ RETORNA DADOS REAIS
    return UserResponse(
        id=user['id'],
        email=user['email'],
        first_name=user.get('first_name'),
        last_name=user.get('last_name'),
        status=user['status'],
        plan=user['plan'],
        created_at=user['created_at']
    )
```

### 2. Supabase Connection Validation

```python
# src/core/supabase_db.py - VALIDAÇÃO DE CONEXÃO
class SupabaseDB:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        
        # ✅ VALIDAÇÃO OBRIGATÓRIA
        if not self.url or not self.service_key:
            raise ValueError("Missing required Supabase environment variables")
        
        self.client = create_client(self.url, self.service_key)
        
        # ✅ TESTE DE CONEXÃO
        self._validate_connection()
    
    def _validate_connection(self):
        """Valida conexão com Supabase"""
        try:
            # Testa consulta simples
            result = self.client.table('users').select('id').limit(1).execute()
            if not hasattr(result, 'data'):
                raise Exception("Invalid Supabase response")
        except Exception as e:
            raise Exception(f"Supabase connection failed: {e}")
```

### 3. Frontend Integration

```typescript
// frontend/src/contexts/AuthContext.tsx - INTEGRAÇÃO CORRETA
const fetchUserData = async (authToken: string) => {
  try {
    setIsLoading(true);
    // ✅ CHAMA API REAL
    const userData = await authApi.me();
    
    // ✅ VALIDA DADOS RECEBIDOS
    if (!userData.email || userData.email === 'user@example.com') {
      throw new Error('API returning mock data');
    }
    
    setUser(userData);
  } catch (error: any) {
    console.error('Failed to fetch user data:', error);
    if (error.response?.status === 401) {
      logout();
    }
  } finally {
    setIsLoading(false);
  }
};
```

## Data Models

### User Model (Real Data)
```typescript
interface UserResponse {
  id: string;                    // UUID real do Supabase
  email: string;                 // Email real do usuário
  first_name: string | null;     // Nome real
  last_name: string | null;      // Sobrenome real
  status: 'active' | 'inactive'; // Status real
  plan: string;                  // Plano real
  created_at: string;            // Data real de criação
}
```

### Expected User Data
```json
{
  "id": "9eadc58c-4dd0-4ce6-9dd4-1cf55169c9db",
  "email": "oguigodomingos@gmail.com",
  "first_name": "Guigo",
  "last_name": "Domingos",
  "status": "active",
  "plan": "free",
  "created_at": "2025-01-08T..."
}
```

## Error Handling

### 1. Database Connection Errors
```python
# Erro de conexão com Supabase
if not supabase_connection:
    raise HTTPException(
        status_code=500, 
        detail="Database connection failed"
    )
```

### 2. User Not Found
```python
# Usuário não encontrado no banco
if not user:
    raise HTTPException(
        status_code=404, 
        detail="User not found"
    )
```

### 3. Invalid Token
```python
# Token JWT inválido
if not token_valid:
    raise HTTPException(
        status_code=401, 
        detail="Invalid or expired token"
    )
```

## Testing Strategy

### 1. Unit Tests
- Test `get_current_user` endpoint with real database
- Test Supabase connection validation
- Test JWT token verification

### 2. Integration Tests
- Test complete auth flow: login → get user data
- Test frontend-backend integration
- Test error scenarios

### 3. End-to-End Tests
```python
# scripts/test_fixed_auth.py
def test_complete_auth_flow():
    # 1. Login with real credentials
    login_response = requests.post(f"{api_url}/auth/login", json={
        "email": "oguigodomingos@gmail.com",
        "password": "180121430"
    })
    assert login_response.status_code == 200
    
    # 2. Get user data
    token = login_response.json()['access_token']
    me_response = requests.get(f"{api_url}/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert me_response.status_code == 200
    
    # 3. Validate real data (not mock)
    user_data = me_response.json()
    assert user_data['email'] == 'oguigodomingos@gmail.com'
    assert user_data['first_name'] == 'Guigo'
    assert user_data['last_name'] == 'Domingos'
    assert user_data['email'] != 'user@example.com'  # Not mock data
```

## Deployment Strategy

### 1. Environment Variables
```bash
# Vercel Environment Variables
SUPABASE_URL=https://roezccmxctqbvdjlgdru.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
JWT_SECRET=dev-jwt-secret-change-in-production
CORS_ORIGINS=https://new-deployment.vercel.app,http://localhost:3000
```

### 2. Deployment Steps
1. Fix authentication implementation
2. Validate Supabase connection
3. Test locally
4. Deploy to Vercel
5. Configure environment variables
6. Test production deployment
7. Validate user authentication

### 3. Rollback Plan
- Keep current working deployment as backup
- Test new deployment thoroughly
- Have database backup ready
- Monitor error logs after deployment

## Security Considerations

### 1. JWT Token Security
- Validate token signature
- Check token expiration
- Verify user exists in database

### 2. Database Security
- Use service role key securely
- Implement RLS policies
- Validate user permissions

### 3. CORS Configuration
- Allow only trusted origins
- Configure proper headers
- Validate request origins

## Performance Considerations

### 1. Database Queries
- Cache user data when possible
- Use efficient queries
- Implement connection pooling

### 2. API Response Times
- Optimize authentication flow
- Minimize database calls
- Use appropriate timeouts

## Monitoring and Logging

### 1. Authentication Logs
- Log successful logins
- Log failed authentication attempts
- Monitor API response times

### 2. Error Tracking
- Track database connection errors
- Monitor JWT validation failures
- Alert on authentication issues