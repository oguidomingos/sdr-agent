from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.db import get_db, User, UserStatus
from src.config.settings import settings
from src.types.auth_schemas import TokenData

# Security
security = HTTPBearer()

class AuthService:
    """
    Serviço de autenticação JWT para o sistema multi-tenant
    """
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = "HS256"
        self.access_token_expire_hours = getattr(settings, 'JWT_EXPIRATION_HOURS', 24)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Cria um token JWT de acesso
        
        Args:
            data: Dados para incluir no token
            expires_delta: Tempo de expiração customizado
            
        Returns:
            str: Token JWT
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=self.access_token_expire_hours)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> TokenData:
        """
        Verifica e decodifica um token JWT
        
        Args:
            token: Token JWT para verificar
            
        Returns:
            TokenData: Dados extraídos do token
            
        Raises:
            HTTPException: Se token inválido
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            
            if user_id is None:
                raise credentials_exception
                
            token_data = TokenData(user_id=user_id, email=email)
            return token_data
            
        except jwt.PyJWTError:
            raise credentials_exception
    
    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """
        Busca usuário por ID
        
        Args:
            db: Sessão do banco
            user_id: ID do usuário
            
        Returns:
            User: Usuário encontrado ou None
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        Busca usuário por email
        
        Args:
            db: Sessão do banco
            email: Email do usuário
            
        Returns:
            User: Usuário encontrado ou None
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """
        Autentica usuário com email e senha
        
        Args:
            db: Sessão do banco
            email: Email do usuário
            password: Senha do usuário
            
        Returns:
            User: Usuário autenticado ou None
        """
        user = await self.get_user_by_email(db, email)
        if not user:
            return None
        if not user.verify_password(password):
            return None
        return user
    
    async def create_user(
        self, 
        db: AsyncSession, 
        email: str, 
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        **kwargs
    ) -> User:
        """
        Cria um novo usuário
        
        Args:
            db: Sessão do banco
            email: Email do usuário
            password: Senha do usuário
            first_name: Primeiro nome
            last_name: Último nome
            **kwargs: Outros campos opcionais
            
        Returns:
            User: Usuário criado
            
        Raises:
            HTTPException: Se email já existe
        """
        # Verifica se email já existe
        existing_user = await self.get_user_by_email(db, email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Cria usuário
        hashed_password = User.hash_password(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            **kwargs
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user

# Instância global do serviço
auth_service = AuthService()

# Dependency para obter usuário atual
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency que extrai e valida o usuário atual do token JWT
    
    Args:
        credentials: Credenciais HTTP Bearer
        db: Sessão do banco
        
    Returns:
        User: Usuário atual autenticado
        
    Raises:
        HTTPException: Se token inválido ou usuário não encontrado
    """
    token_data = auth_service.verify_token(credentials.credentials)
    user = await auth_service.get_user_by_id(db, token_data.user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Atualiza último login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    return user

# Dependency para usuário ativo
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency que garante que o usuário está ativo
    
    Args:
        current_user: Usuário atual
        
    Returns:
        User: Usuário ativo
        
    Raises:
        HTTPException: Se usuário inativo
    """
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

# Utility functions
def create_user_token(user: User) -> Dict[str, Any]:
    """
    Cria token de acesso para usuário
    
    Args:
        user: Usuário para criar token
        
    Returns:
        dict: Dados do token
    """
    access_token_expires = timedelta(hours=auth_service.access_token_expire_hours)
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds())
    }