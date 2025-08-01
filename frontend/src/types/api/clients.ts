export interface ClientResponse {
  id: string;
  name: string;
  description?: string;
  domain: string;
  status: 'TRIAL' | 'ACTIVE' | 'SUSPENDED' | 'CANCELLED';
  evolution_api_url?: string;
  evolution_api_key?: string;
  evolution_instance?: string;
  gemini_api_key?: string;
  gemini_model?: string;
  session_timeout?: number;
  max_history?: number;
  context_window_size?: number;
  agent_name?: string;
  agent_persona?: string;
  welcome_message?: string;
  logo_url?: string;
  contact_email?: string;
  contact_phone?: string;
  business_hours?: string;
  timezone?: string;
  ai_temperature?: number;
  rate_limit_enabled?: boolean;
  rate_limit_calls?: number;
  rate_limit_period?: number;
  has_webhook_configured: boolean;
  created_at: string;
  updated_at: string;
}

export interface ClientListResponse {
  clients: ClientResponse[];
  total: number;
  skip: number;
  limit: number;
}

export interface ClientCreate {
  name: string;
  description?: string;
  domain: string;
  evolution_api_url?: string;
  evolution_api_key?: string;
  evolution_instance?: string;
  gemini_api_key?: string;
  gemini_model?: string;
  session_timeout?: number;
  max_history?: number;
  context_window_size?: number;
  agent_name?: string;
  agent_persona?: string;
  welcome_message?: string;
  logo_url?: string;
  contact_email?: string;
  contact_phone?: string;
  business_hours?: string;
  timezone?: string;
  ai_temperature?: number;
  rate_limit_enabled?: boolean;
  rate_limit_calls?: number;
  rate_limit_period?: number;
  create_default_playbook?: boolean;
  register_webhook?: boolean;
}

export interface ClientUpdate {
  name?: string;
  description?: string;
  domain?: string;
  evolution_api_url?: string;
  evolution_api_key?: string;
  evolution_instance?: string;
  gemini_api_key?: string;
  gemini_model?: string;
  session_timeout?: number;
  max_history?: number;
  context_window_size?: number;
  agent_name?: string;
  agent_persona?: string;
  welcome_message?: string;
  logo_url?: string;
  contact_email?: string;
  contact_phone?: string;
  business_hours?: string;
  timezone?: string;
  ai_temperature?: number;
  rate_limit_enabled?: boolean;
  rate_limit_calls?: number;
  rate_limit_period?: number;
  register_webhook?: boolean;
}