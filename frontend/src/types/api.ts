// Types based on our backend schemas
export interface Client {
  id: string;
  name: string;
  description?: string;
  domain: string;
  status: 'active' | 'inactive' | 'suspended' | 'trial';
  
  // WhatsApp Configuration
  whatsapp_number?: string;
  
  // API Configuration
  evolution_api_url?: string;
  evolution_api_key?: string;
  evolution_instance?: string;
  gemini_api_key?: string;
  gemini_model?: string;
  
  // Session Configuration
  session_timeout: number;
  max_history: number;
  context_window_size: number;
  
  // Persona and Branding
  agent_name: string;
  agent_persona?: string;
  welcome_message?: string;
  logo_url?: string;
  
  // Business Information
  contact_email?: string;
  contact_phone?: string;
  business_hours?: Record<string, any>;
  timezone: string;
  
  // Settings
  ai_temperature: number;
  rate_limit_enabled: boolean;
  rate_limit_calls: number;
  rate_limit_period: number;
  
  // Webhook
  has_webhook_configured: boolean;
  
  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface Playbook {
  id: string;
  client_id: string;
  name: string;
  description?: string;
  status: 'draft' | 'active' | 'archived';
  is_default: boolean;
  version: number;
  
  // Conversation Flow
  steps: Array<Record<string, any>>;
  conditions?: Record<string, any>;
  fallback_messages?: string[];
  
  // SPIN Selling Configuration
  situation_prompts?: string[];
  problem_prompts?: string[];
  implication_prompts?: string[];
  need_payoff_prompts?: string[];
  
  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  client_id: string;
  user_id: string;
  user_name?: string;
  message_direction: 'inbound' | 'outbound';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
  status?: string;
  conversation_stage?: string;
  lead_score: number;
}

export interface Conversation {
  user_id: string;
  user_name?: string;
  client_id: string;
  messages: Message[];
  last_interaction: string;
  message_count: number;
  status?: string;
  lead_score: number;
}

// API Response types
export interface ClientListResponse {
  clients: Client[];
  total: number;
  skip: number;
  limit: number;
}

export interface PlaybookListResponse {
  playbooks: Playbook[];
  total: number;
  skip: number;
  limit: number;
}

export interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
  skip: number;
  limit: number;
}

export interface MessageHistoryResponse {
  messages: Message[];
  total: number;
  skip: number;
  limit: number;
}

// Form types
export interface ClientCreateData {
  name: string;
  description?: string;
  domain: string;
  whatsapp_number: string;  // Campo obrigatório
  evolution_api_url: string;
  evolution_api_key: string;
  gemini_api_key: string;
  gemini_model?: string;
  session_timeout?: number;
  max_history?: number;
  context_window_size?: number;
  agent_name?: string;
  agent_prompt?: string;  // Changed from agent_persona to agent_prompt
  agent_persona?: string;
  welcome_message?: string;
  logo_url?: string;
  contact_email?: string;
  contact_phone?: string;
  business_hours?: Record<string, any>;
  timezone?: string;
  ai_temperature?: number;  // Frontend will convert 0.7 to 70 before sending
  rate_limit_enabled?: boolean;
  rate_limit_calls?: number;
  rate_limit_period?: number;
  create_default_playbook?: boolean;
  register_webhook?: boolean;
  
  // Agent batch configuration (required in backend)
  batch_enabled: boolean;
  batch_window_seconds: number;
}

export interface ClientUpdateData extends Partial<ClientCreateData> {
  status?: 'active' | 'inactive' | 'suspended' | 'trial';
  register_webhook?: boolean;
}

export interface PlaybookCreateData {
  client_id: string;
  name: string;
  description?: string;
  is_default?: boolean;
  steps?: Array<Record<string, any>>;
  conditions?: Record<string, any>;
  fallback_messages?: string[];
  situation_prompts?: string[];
  problem_prompts?: string[];
  implication_prompts?: string[];
  need_payoff_prompts?: string[];
}

export interface PlaybookUpdateData extends Partial<PlaybookCreateData> {
  status?: 'draft' | 'active' | 'archived';
}

// Authentication types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  email: string;
  first_name: string;
  last_name?: string;
  status: string;
  plan: string;
  max_clients: number;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

// Stats for História 4
export interface StatsResponse {
  total_conversations: number;
  leads_qualified: number;
  appointments_scheduled: number;
  period_start?: string;
  period_end?: string;
}

// Dashboard statistics
export interface DashboardStats {
  total_clients: number;
  active_conversations: number;
  total_messages: number;
  leads_qualified: number;
  conversion_rate: number;
  recent_conversations: Array<{
    user_id: string;
    user_name?: string;
    last_message: string;
    timestamp: string;
    status?: string;
  }>;
}