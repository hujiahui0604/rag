import axios, { AxiosError } from 'axios';

const API_BASE_URL = (import.meta as ImportMeta & { env: Record<string, string> }).env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Document {
  id: number;
  title: string;
  description?: string;
  file_type: string;
  file_size: number;
  status: string;
  chunk_count: number;
  category_id?: number;
  created_by: number;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  items: Document[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  parent_id?: number;
  created_by: number;
  created_at: string;
}

export interface ChatSession {
  id: number;
  title?: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  role: string;
  content: string;
  session_id: number;
  token_count: number;
  created_at: string;
}

export interface ChatRequest {
  message: string;
  session_id?: number;
  use_history?: boolean;
}

export interface ChatResponse {
  message: string;
  sources?: Array<{
    text: string;
    score: number;
    document_id: number;
  }>;
  session_id: number;
  token_count: number;
}

export const authApi = {
  login: (data: LoginRequest) => {
    const params = new URLSearchParams();
    params.append('username', data.username);
    params.append('password', data.password);
    return api.post<TokenResponse>('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  register: (data: RegisterRequest) =>
    api.post<User>('/auth/register', data),
  me: () => api.get<User>('/auth/me'),
};

export const documentApi = {
  list: (params?: { page?: number; page_size?: number; search?: string; category_id?: number }) =>
    api.get<DocumentListResponse>('/documents', { params }),
  get: (id: number) => api.get<Document>(`/documents/${id}`),
  create: (formData: FormData) =>
    api.post<Document>('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  update: (id: number, data: { title?: string; description?: string; category_id?: number }) =>
    api.put<Document>(`/documents/${id}`, data),
  index: (id: number) => api.post<Document>(`/documents/${id}/index`),
  delete: (id: number) => api.delete(`/documents/${id}`),
};

export const categoryApi = {
  list: (parentId?: number) => api.get<Category[]>('/categories', { params: { parent_id: parentId } }),
  create: (data: { name: string; description?: string; parent_id?: number }) =>
    api.post<Category>('/categories', data),
  update: (id: number, data: { name?: string; description?: string }) =>
    api.put<Category>(`/categories/${id}`, data),
  delete: (id: number) => api.delete(`/categories/${id}`),
};

export const chatApi = {
  listSessions: () => api.get<ChatSession[]>('/chat/sessions'),
  createSession: (data: { title?: string }) => api.post<ChatSession>('/chat/sessions', data),
  getMessages: (sessionId: number) => api.get<ChatMessage[]>(`/chat/sessions/${sessionId}`),
  sendMessage: (data: ChatRequest) => api.post<ChatResponse>('/chat/message', data),
};

export default api;