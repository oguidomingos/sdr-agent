-- Create ENUM types first
CREATE TYPE userstatus AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE clientstatus AS ENUM ('active', 'inactive', 'suspended', 'trial');
CREATE TYPE playbookstatus AS ENUM ('DRAFT', 'ACTIVE', 'ARCHIVED');
CREATE TYPE message_direction AS ENUM ('inbound', 'outbound');
CREATE TYPE message_status AS ENUM ('qualified', 'scheduled', 'none', 'lost', 'archived');

-- Create users table
CREATE TABLE users (
    id VARCHAR NOT NULL,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    status userstatus,
    plan VARCHAR(50),
    max_clients INTEGER,
    timezone VARCHAR(50),
    language VARCHAR(10),
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE,
    last_login TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (id)
);

-- Create clients table
CREATE TABLE clients (
    id VARCHAR NOT NULL,
    owner_id VARCHAR NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    domain VARCHAR(255),
    status clientstatus,
    evolution_api_url VARCHAR(500),
    evolution_api_key VARCHAR(500),
    evolution_instance VARCHAR(100),
    evolution_instance_id VARCHAR(100),
    evolution_instance_token VARCHAR(500),
    gemini_api_key VARCHAR(500),
    gemini_model VARCHAR(100),
    agent_prompt TEXT,
    agent_name VARCHAR(100),
    agent_persona TEXT,
    welcome_message TEXT,
    webhook_secret VARCHAR(255),
    webhook_url VARCHAR(500),
    session_timeout INTEGER,
    max_history INTEGER,
    context_window_size INTEGER,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    business_hours JSON,
    timezone VARCHAR(50),
    logo_url VARCHAR(500),
    ai_temperature INTEGER,
    rate_limit_enabled BOOLEAN,
    rate_limit_calls INTEGER,
    rate_limit_period INTEGER,
    db_connection_uri VARCHAR(1000),
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (id),
    FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE CASCADE,
    UNIQUE (domain)
);

-- Create playbooks table
CREATE TABLE playbooks (
    id VARCHAR NOT NULL,
    client_id VARCHAR NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status playbookstatus,
    is_default BOOLEAN,
    version INTEGER,
    steps JSON,
    conditions JSON,
    fallback_messages JSON,
    situation_prompts JSON,
    problem_prompts JSON,
    implication_prompts JSON,
    need_payoff_prompts JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (id),
    FOREIGN KEY(client_id) REFERENCES clients (id) ON DELETE CASCADE
);

-- Create agent_configs table
CREATE TABLE agent_configs (
    id VARCHAR NOT NULL,
    client_id VARCHAR NOT NULL,
    name VARCHAR(255) NOT NULL,
    version INTEGER,
    is_active BOOLEAN,
    system_prompt TEXT,
    welcome_prompt TEXT,
    fallback_prompt TEXT,
    situation_prompts JSON,
    problem_prompts JSON,
    implication_prompts JSON,
    need_payoff_prompts JSON,
    temperature INTEGER,
    max_tokens INTEGER,
    top_p INTEGER,
    batch_enabled BOOLEAN,
    batch_window_seconds INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (id),
    FOREIGN KEY(client_id) REFERENCES clients (id) ON DELETE CASCADE
);

-- Create messages table
CREATE TABLE messages (
    id VARCHAR NOT NULL,
    client_id VARCHAR NOT NULL,
    user_id VARCHAR,
    user_name VARCHAR(255),
    message_direction message_direction,
    content TEXT,
    timestamp TIMESTAMP WITHOUT TIME ZONE,
    message_metadata JSON,
    status message_status,
    conversation_stage VARCHAR(50),
    lead_score INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY(client_id) REFERENCES clients (id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_user_status ON users (status);
CREATE INDEX ix_users_id ON users (id);
CREATE INDEX idx_user_email ON users (email);
CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE INDEX idx_client_status ON clients (status);
CREATE INDEX idx_client_owner ON clients (owner_id);
CREATE INDEX ix_clients_owner_id ON clients (owner_id);
CREATE INDEX ix_clients_id ON clients (id);
CREATE INDEX idx_client_domain ON clients (domain);

CREATE INDEX idx_playbook_default ON playbooks (client_id, is_default);
CREATE INDEX idx_playbook_status ON playbooks (status);
CREATE INDEX ix_playbooks_id ON playbooks (id);
CREATE INDEX idx_playbook_client ON playbooks (client_id);

CREATE INDEX idx_agent_config_client ON agent_configs (client_id);
CREATE INDEX idx_agent_config_active ON agent_configs (client_id, is_active);
CREATE INDEX ix_agent_configs_id ON agent_configs (id);

CREATE INDEX idx_message_client_user ON messages (client_id, user_id);
CREATE INDEX idx_message_timestamp ON messages (timestamp);
CREATE INDEX idx_message_status ON messages (status);
CREATE INDEX idx_message_conversation_stage ON messages (conversation_stage);
CREATE INDEX ix_messages_id ON messages (id);
CREATE INDEX ix_messages_client_id ON messages (client_id);