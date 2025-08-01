-- SDR Agent Multi-Client SaaS Schema Migration for Supabase
-- This script creates all necessary tables and RLS policies

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE client_status AS ENUM ('active', 'inactive', 'suspended', 'trial');
CREATE TYPE message_direction AS ENUM ('inbound', 'outbound');
CREATE TYPE message_status AS ENUM ('qualified', 'scheduled', 'none', 'lost', 'archived');
CREATE TYPE playbook_status AS ENUM ('draft', 'active', 'archived');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    status user_status DEFAULT 'active',
    plan VARCHAR(50) DEFAULT 'free',
    max_clients INTEGER DEFAULT 10,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'pt-BR',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Clients table
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    domain VARCHAR(255) UNIQUE,
    status client_status DEFAULT 'trial',
    
    -- WhatsApp Configuration
    whatsapp_number VARCHAR(20),
    
    -- Evolution API Configuration
    evolution_api_url VARCHAR(500),
    evolution_api_key VARCHAR(500),
    evolution_instance VARCHAR(100),
    evolution_instance_id VARCHAR(100),
    evolution_instance_token VARCHAR(500),
    
    -- AI Configuration
    gemini_api_key VARCHAR(500),
    gemini_model VARCHAR(100) DEFAULT 'gemini-2.0-flash',
    
    -- Agent Configuration
    agent_prompt TEXT,
    agent_name VARCHAR(100) DEFAULT 'Assistente',
    agent_persona TEXT,
    welcome_message TEXT,
    
    -- Webhook Configuration
    webhook_secret VARCHAR(255),
    webhook_url VARCHAR(500),
    
    -- Session Configuration
    session_timeout INTEGER DEFAULT 3600,
    max_history INTEGER DEFAULT 50,
    context_window_size INTEGER DEFAULT 20,
    
    -- Business Information
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    business_hours JSONB,
    timezone VARCHAR(50) DEFAULT 'UTC',
    logo_url VARCHAR(500),
    
    -- AI Settings
    ai_temperature INTEGER DEFAULT 70,
    rate_limit_enabled BOOLEAN DEFAULT TRUE,
    rate_limit_calls INTEGER DEFAULT 100,
    rate_limit_period INTEGER DEFAULT 3600,
    
    -- Database Configuration
    db_connection_uri VARCHAR(1000),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Playbooks table
CREATE TABLE playbooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status playbook_status DEFAULT 'draft',
    
    -- Playbook Configuration
    is_default BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1,
    
    -- Conversation Flow
    steps JSONB,
    conditions JSONB,
    fallback_messages JSONB,
    
    -- SPIN Selling Configuration
    situation_prompts JSONB,
    problem_prompts JSONB,
    implication_prompts JSONB,
    need_payoff_prompts JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Configs table
CREATE TABLE agent_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(255) NOT NULL,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Prompt Configuration
    system_prompt TEXT,
    welcome_prompt TEXT,
    fallback_prompt TEXT,
    
    -- SPIN Selling Prompts
    situation_prompts JSONB,
    problem_prompts JSONB,
    implication_prompts JSONB,
    need_payoff_prompts JSONB,
    
    -- AI Parameters
    temperature INTEGER DEFAULT 70,
    max_tokens INTEGER DEFAULT 1000,
    top_p INTEGER DEFAULT 95,
    
    -- Batch Processing Config
    batch_enabled BOOLEAN DEFAULT TRUE,
    batch_window_seconds INTEGER DEFAULT 180,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE NOT NULL,
    user_id VARCHAR(255),
    user_name VARCHAR(255),
    message_direction message_direction,
    content TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    message_metadata JSONB,
    status message_status DEFAULT 'none',
    
    -- Message Context
    conversation_stage VARCHAR(50),
    lead_score INTEGER DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);

CREATE INDEX idx_clients_owner ON clients(owner_id);
CREATE INDEX idx_clients_domain ON clients(domain);
CREATE INDEX idx_clients_status ON clients(status);

CREATE INDEX idx_playbooks_client ON playbooks(client_id);
CREATE INDEX idx_playbooks_status ON playbooks(status);
CREATE INDEX idx_playbooks_default ON playbooks(client_id, is_default);

CREATE INDEX idx_agent_configs_client ON agent_configs(client_id);
CREATE INDEX idx_agent_configs_active ON agent_configs(client_id, is_active);

CREATE INDEX idx_messages_client_user ON messages(client_id, user_id);
CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_status ON messages(status);
CREATE INDEX idx_messages_conversation_stage ON messages(conversation_stage);
CREATE INDEX idx_messages_client_timestamp ON messages(client_id, timestamp DESC);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE playbooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies for Users
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- RLS Policies for Clients
CREATE POLICY "Users can manage own clients" ON clients
    FOR ALL USING (owner_id::text = auth.uid()::text);

-- RLS Policies for Playbooks
CREATE POLICY "Users can manage playbooks of own clients" ON playbooks
    FOR ALL USING (
        client_id IN (
            SELECT id FROM clients WHERE owner_id::text = auth.uid()::text
        )
    );

-- RLS Policies for Agent Configs
CREATE POLICY "Users can manage agent configs of own clients" ON agent_configs
    FOR ALL USING (
        client_id IN (
            SELECT id FROM clients WHERE owner_id::text = auth.uid()::text
        )
    );

-- RLS Policies for Messages
CREATE POLICY "Users can manage messages of own clients" ON messages
    FOR ALL USING (
        client_id IN (
            SELECT id FROM clients WHERE owner_id::text = auth.uid()::text
        )
    );

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON clients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_playbooks_updated_at BEFORE UPDATE ON playbooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_configs_updated_at BEFORE UPDATE ON agent_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();