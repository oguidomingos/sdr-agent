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
  DashboardStats,
} from '@/types/api';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000',
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
    return Promise.reject(error);
  }
);

// Authentication API functions
export const authApi = {
  login: async (email: string, password: string): Promise<{ access_token: string; token_type: string; expires_in: number }> => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (email: string, password: string, first_name: string, last_name?: string) => {
    const response = await api.post('/auth/register', { 
      email, 
      password, 
      first_name, 
      last_name 
    });
    return response.data;
  },

  me: async () => {
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
};

// Playbook API functions
export const playbooksApi = {
  getAll: async (
    client_id?: string,
    skip = 0,
    limit = 100
  ): Promise<PlaybookListResponse> => {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });
    if (client_id) {
      params.append('client_id', client_id);
    }
    const response = await api.get(`/playbooks?${params}`);
    return response.data;
  },

  getById: async (id: string): Promise<Playbook> => {
    const response = await api.get(`/playbooks/${id}`);
    return response.data;
  },

  create: async (data: PlaybookCreateData): Promise<Playbook> => {
    const response = await api.post('/playbooks', data);
    return response.data;
  },

  update: async (id: string, data: PlaybookUpdateData): Promise<Playbook> => {
    const response = await api.put(`/playbooks/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/playbooks/${id}`);
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