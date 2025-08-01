from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import Column, String, DateTime, JSON, Enum, Integer, Boolean, Text, ForeignKey, Index, text
import enum
from datetime import datetime
import uuid
from passlib.context import CryptContext

from src.config.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class MessageDirection(str, enum.Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class MessageStatus(enum.Enum):
    QUALIFIED = "qualified"
    SCHEDULED = "scheduled"
    NONE = "none"
    LOST = "lost"
    ARCHIVED = "archived"

class ClientStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"

class PlaybookStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    status = Column(Enum(UserStatus, values_callable=lambda obj: [e.value for e in obj]), default=UserStatus.ACTIVE)
    
    # Subscription/Plan info
    plan = Column(String(50), default="free")  # free, basic, premium
    max_clients = Column(Integer, default=10)  # limit based on plan (increased for testing)
    
    # Settings
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="pt-BR")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    clients = relationship("Client", back_populates="owner", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_status', 'status'),
    )
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(password, self.hashed_password)
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash password for storage"""
        return pwd_context.hash(password)

class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    owner_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    domain = Column(String(255), unique=True)
    status = Column(Enum(ClientStatus, values_callable=lambda obj: [e.value for e in obj]), default=ClientStatus.TRIAL)
    
    # WhatsApp Configuration
    whatsapp_number = Column(String(20))  # Número do WhatsApp conectado
    
    # Evolution API Configuration
    evolution_api_url = Column(String(500))
    evolution_api_key = Column(String(500))
    evolution_instance = Column(String(100))
    evolution_instance_id = Column(String(100))  # ID retornado pela Evolution API
    evolution_instance_token = Column(String(500))  # Token da instância
    
    # AI Configuration
    gemini_api_key = Column(String(500))
    gemini_model = Column(String(100), default="gemini-2.0-flash")
    
    # Agent Configuration
    agent_prompt = Column(Text)  # Prompt base do agente
    agent_name = Column(String(100), default="Assistente")
    agent_persona = Column(Text)
    welcome_message = Column(Text)
    
    # Webhook Configuration
    webhook_secret = Column(String(255))  # Secret para validar webhooks
    webhook_url = Column(String(500))  # URL customizada se necessário
    
    # Session Configuration
    session_timeout = Column(Integer, default=3600)
    max_history = Column(Integer, default=50)
    context_window_size = Column(Integer, default=20)
    
    # Business Information
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    business_hours = Column(JSON)
    timezone = Column(String(50), default="UTC")
    logo_url = Column(String(500))
    
    # AI Settings
    ai_temperature = Column(Integer, default=70)  # 0-100 scale
    rate_limit_enabled = Column(Boolean, default=True)
    rate_limit_calls = Column(Integer, default=100)
    rate_limit_period = Column(Integer, default=3600)
    
    # Database Configuration (para futuro isolamento)
    db_connection_uri = Column(String(1000))  # URI do banco dedicado (opcional)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="clients")
    messages = relationship("Message", back_populates="client", cascade="all, delete-orphan")
    playbooks = relationship("Playbook", back_populates="client", cascade="all, delete-orphan")
    agent_configs = relationship("AgentConfig", back_populates="client", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_client_owner', 'owner_id'),
        Index('idx_client_domain', 'domain'),
        Index('idx_client_status', 'status'),
    )

class Playbook(Base):
    __tablename__ = "playbooks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(PlaybookStatus), default=PlaybookStatus.DRAFT)
    
    # Playbook Configuration
    is_default = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    
    # Conversation Flow
    steps = Column(JSON)  # Array of conversation steps
    conditions = Column(JSON)  # Conditional logic for flow
    fallback_messages = Column(JSON)  # Fallback responses
    
    # SPIN Selling Configuration
    situation_prompts = Column(JSON)
    problem_prompts = Column(JSON)
    implication_prompts = Column(JSON)
    need_payoff_prompts = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="playbooks")
    
    __table_args__ = (
        Index('idx_playbook_client', 'client_id'),
        Index('idx_playbook_status', 'status'),
        Index('idx_playbook_default', 'client_id', 'is_default'),
    )

class AgentConfig(Base):
    __tablename__ = "agent_configs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Prompt Configuration
    system_prompt = Column(Text)  # Prompt do sistema
    welcome_prompt = Column(Text)  # Mensagem de boas-vindas
    fallback_prompt = Column(Text)  # Resposta quando não entende
    
    # SPIN Selling Prompts (herdado do Playbook)
    situation_prompts = Column(JSON)
    problem_prompts = Column(JSON)
    implication_prompts = Column(JSON)
    need_payoff_prompts = Column(JSON)
    
    # AI Parameters
    temperature = Column(Integer, default=70)  # 0-100
    max_tokens = Column(Integer, default=1000)
    top_p = Column(Integer, default=95)  # 0-100
    
    # Batch Processing Config
    batch_enabled = Column(Boolean, default=True)
    batch_window_seconds = Column(Integer, default=180)  # 3 minutos
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="agent_configs")
    
    __table_args__ = (
        Index('idx_agent_config_client', 'client_id'),
        Index('idx_agent_config_active', 'client_id', 'is_active'),
    )

class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, index=True)
    user_name = Column(String(255))
    message_direction = Column(Enum(MessageDirection, name='message_direction', values_callable=lambda obj: [e.value for e in obj]))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    message_metadata = Column(JSON)
    status = Column(Enum(MessageStatus, name='message_status', values_callable=lambda obj: [e.value for e in obj]), default=MessageStatus.NONE)
    
    # Message Context
    conversation_stage = Column(String(50))  # e.g., 'situation', 'problem', 'implication'
    lead_score = Column(Integer, default=0)  # 0-100 scoring
    
    # Relationships
    client = relationship("Client", back_populates="messages")
    
    __table_args__ = (
        Index('idx_message_client_user', 'client_id', 'user_id'),
        Index('idx_message_timestamp', 'timestamp'),
        Index('idx_message_status', 'status'),
        Index('idx_message_conversation_stage', 'conversation_stage'),
    )

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database tables and create indexes"""
    try:
        # Use begin() and explicitly commit to ensure tables are persisted
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Base tables created")
            
        # Verify tables were created
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Tables in database: {tables}")
            
            if not tables:
                print("⚠️  No tables found, trying alternative creation method")
                # Alternative method: create without transaction
                await conn.run_sync(Base.metadata.create_all)
                await conn.commit()
        
        # Create additional indexes in separate connection
        try:
            async with engine.connect() as conn:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_messages_client_timestamp 
                    ON messages (client_id, timestamp DESC);
                """))
                
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_messages_user_recent 
                    ON messages (user_id, timestamp DESC) 
                    WHERE timestamp > NOW() - INTERVAL '30 days';
                """))
                await conn.commit()
                print("✅ Additional indexes created")
        except Exception as e:
            print(f"Warning: Could not create additional indexes: {e}")
            
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise

async def seed_default_data():
    """Seed database with default data for development"""
    try:
        # Wait a bit to ensure tables are committed
        import asyncio
        await asyncio.sleep(0.5)
        
        async with AsyncSessionLocal() as session:
            # Check if we already have a default client
            from sqlalchemy import select
            try:
                result = await session.execute(select(Client).where(Client.domain == "demo.sdr-agent.com"))
                existing_client = result.scalar_one_or_none()
            except Exception as e:
                print(f"⚠️  Error checking existing client, assuming none exists: {e}")
                existing_client = None
            
            if not existing_client:
                # Create default demo client
                demo_client = Client(
                    name="Demo Medical Clinic",
                    description="Demo client for testing and development",
                    domain="demo.sdr-agent.com",
                    status=ClientStatus.ACTIVE,
                    agent_name="Dr. Assistant",
                    agent_persona="Sou um assistente especializado em atendimento médico, usando a metodologia SPIN Selling para qualificar leads interessados em consultas.",
                    welcome_message="Olá! Sou o Dr. Assistant. Como posso ajudá-lo hoje?",
                    contact_email="demo@sdr-agent.com",
                    business_hours={
                        "monday": {"open": "08:00", "close": "18:00"},
                        "tuesday": {"open": "08:00", "close": "18:00"},
                        "wednesday": {"open": "08:00", "close": "18:00"},
                        "thursday": {"open": "08:00", "close": "18:00"},
                        "friday": {"open": "08:00", "close": "17:00"},
                        "saturday": {"open": "09:00", "close": "13:00"},
                        "sunday": {"closed": True}
                    }
                )
                session.add(demo_client)
                await session.commit()
                
                # Create default playbook for demo client
                default_playbook = Playbook(
                    client_id=demo_client.id,
                    name="Medical SPIN Selling Playbook",
                    description="Default playbook using SPIN methodology for medical consultations",
                    status=PlaybookStatus.ACTIVE,
                    is_default=True,
                    steps=[
                        {"stage": "welcome", "message": "Olá! Como posso ajudá-lo?", "next": "situation"},
                        {"stage": "situation", "prompt": "Descubra a situação atual do paciente", "next": "problem"},
                        {"stage": "problem", "prompt": "Identifique os problemas específicos", "next": "implication"},
                        {"stage": "implication", "prompt": "Explore as implicações dos problemas", "next": "need_payoff"},
                        {"stage": "need_payoff", "prompt": "Apresente os benefícios da solução", "next": "close"}
                    ],
                    situation_prompts=[
                        "Há quanto tempo sente esses sintomas?",
                        "Já consultou algum médico sobre isso?",
                        "Como isso está afetando seu dia a dia?"
                    ],
                    problem_prompts=[
                        "Quais são os principais desconfortos?",
                        "Em que momentos os sintomas pioram?",
                        "O que mais te preocupa sobre essa situação?"
                    ],
                    implication_prompts=[
                        "Como isso pode evoluir se não for tratado?",
                        "Que impacto isso pode ter na sua qualidade de vida?",
                        "Quais riscos você vê se adiar o tratamento?"
                    ],
                    need_payoff_prompts=[
                        "Como seria sua vida sem esses sintomas?",
                        "Qual a importância de resolver isso agora?",
                        "O que significaria ter um diagnóstico preciso?"
                    ]
                )
                session.add(default_playbook)
                await session.commit()
                
                print("✅ Default data seeded successfully!")
            else:
                print("ℹ️  Default client already exists, skipping seeding.")
                
    except Exception as e:
        print(f"❌ Error seeding default data: {e}")
        print("⚠️  Application will continue without default data.")
