import axios from 'axios';
import {
  Client,
  ClientListResponse,
  ClientCreateData,
  ClientUpdateData,
  Playbook,
  PlaybookListResponse,
  PlaybookCreateData,
  PlaybookUpdateData,
  ConversationListResponse,
  MessageHistoryResponse,
  StatsResponse,
  DashboardStats,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UserResponse,
} from '@/types/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication if needed
api.interceptors.request.use((config) => {
  // Add auth token if available
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    // Handle unauthorized errors globally
    if (error.response?.status === 401) {
      // Clear authentication data
      localStorage.removeItem('auth_token');
      localStorage.removeItem('selectedClientId');
      
      // Redirect to login if not already on auth page
      if (!window.location.pathname.includes('/auth')) {
        window.location.reload();
      }
    }
    
    return Promise.reject(error);
  }
);

// Authentication API functions
export const authApi = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const loginData: LoginRequest = { email, password };
    const response = await api.post('/auth/login', loginData);
    return response.data;
  },

  register: async (email: string, password: string, first_name: string, last_name?: string): Promise<UserResponse> => {
    const registerData: RegisterRequest = { 
      email, 
      password, 
      first_name, 
      last_name 
    };
    const response = await api.post('/auth/register', registerData);
    return response.data;
  },

  me: async (): Promise<UserResponse> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Client API functions
export const clientsApi = {
  getAll: async (skip = 0, limit = 100): Promise<ClientListResponse> => {
    const response = await api.get(`/clients/?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  getById: async (id: string): Promise<Client> => {
    const response = await api.get(`/clients/${id}`);
    return response.data;
  },

  create: async (data: ClientCreateData): Promise<Client> => {
    const response = await api.post('/clients/', data);
    return response.data;
  },

  update: async (id: string, data: ClientUpdateData): Promise<Client> => {
    const response = await api.put(`/clients/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/clients/${id}`);
  },

  registerWebhook: async (id: string): Promise<void> => {
    await api.post(`/clients/${id}/webhook`);
  },
};

// Playbook API functions
export const playbooksApi = {
  getAll: async (
    client_id: string,
    skip = 0,
    limit = 100
  ): Promise<PlaybookListResponse> => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    const response = await api.get(`/clients/${client_id}/playbooks?${params}`);
    return response.data;
  },

  getById: async (client_id: string, id: string): Promise<Playbook> => {
    const response = await api.get(`/clients/${client_id}/playbooks/${id}`);
    return response.data;
  },

  create: async (client_id: string, data: PlaybookCreateData): Promise<Playbook> => {
    const response = await api.post(`/clients/${client_id}/playbooks`, data);
    return response.data;
  },

  update: async (client_id: string, id: string, data: PlaybookUpdateData): Promise<Playbook> => {
    const response = await api.put(`/clients/${client_id}/playbooks/${id}`, data);
    return response.data;
  },

  delete: async (client_id: string, id: string): Promise<void> => {
    await api.delete(`/clients/${client_id}/playbooks/${id}`);
  },

  activate: async (client_id: string, id: string): Promise<Playbook> => {
    const response = await api.post(`/clients/${client_id}/playbooks/${id}/activate`);
    return response.data;
  },

  deactivate: async (client_id: string, id: string): Promise<Playbook> => {
    const response = await api.post(`/clients/${client_id}/playbooks/${id}/deactivate`);
    return response.data;
  },

  duplicate: async (client_id: string, id: string): Promise<Playbook> => {
    const response = await api.post(`/clients/${client_id}/playbooks/${id}/duplicate`);
    return response.data;
  },
};

// Conversations API functions
export const conversationsApi = {
  getAll: async (
    client_id?: string,
    skip = 0,
    limit = 100
  ): Promise<ConversationListResponse> => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (client_id) {
      params.append('client_id', client_id);
    }
    const response = await api.get(`/conversations?${params}`);
    return response.data;
  },

  getMessages: async (
    user_id: string,
    client_id?: string,
    skip = 0,
    limit = 100
  ): Promise<MessageHistoryResponse> => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (client_id) {
      params.append('client_id', client_id);
    }
    const response = await api.get(`/conversations/${user_id}/messages?${params}`);
    return response.data;
  },
};

// Session API functions
export const sessionsApi = {
  get: async (user_id: string) => {
    const response = await api.get(`/sessions/${user_id}`);
    return response.data;
  },

  delete: async (user_id: string): Promise<void> => {
    await api.delete(`/sessions/${user_id}`);
  },
};

// Messages API functions - História 4
export const messagesApi = {
  list: async (
    clientId: string,
    params: {
      date_from?: string;
      date_to?: string;
      status?: string;
      keyword?: string;
      skip?: number;
      limit?: number;
    } = {}
  ): Promise<MessageHistoryResponse> => {
    const searchParams = new URLSearchParams();
    if (params.date_from) searchParams.append('date_from', params.date_from);
    if (params.date_to) searchParams.append('date_to', params.date_to);
    if (params.status) searchParams.append('status', params.status);
    if (params.keyword) searchParams.append('keyword', params.keyword);
    if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
    if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());

    const response = await api.get(`/clients/${clientId}/messages?${searchParams}`);
    return response.data;
  },
};

// Stats API functions - História 4
export const statsApi = {
  get: async (
    clientId: string,
    params: {
      date_from?: string;
      date_to?: string;
    } = {}
  ): Promise<StatsResponse> => {
    const searchParams = new URLSearchParams();
    if (params.date_from) searchParams.append('date_from', params.date_from);
    if (params.date_to) searchParams.append('date_to', params.date_to);

    const response = await api.get(`/clients/${clientId}/stats?${searchParams}`);
    return response.data;
  },
};

// Dashboard API functions
export const dashboardApi = {
  getStats: async (client_id?: string): Promise<DashboardStats> => {
    const params = client_id ? `?client_id=${client_id}` : '';
    const response = await api.get(`/dashboard/stats${params}`);
    return response.data;
  },
};

// Health check
export const healthApi = {
  check: async (): Promise<{ status: string }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;