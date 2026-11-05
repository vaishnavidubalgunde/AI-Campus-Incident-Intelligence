import axios from 'axios';
import {
  AuthResponse,
  User,
  Department,
  IncidentCategory,
  Incident,
  StatsOverview,
  HotspotDashboardData,
  DiscoveredPattern,
  Recommendation,
  AssistantResponse,
  NotificationItem,
  AuditLogItem
} from '../types';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const res = await api.post<AuthResponse>('/auth/login', { email, password });
    return res.data;
  },
  register: async (data: { email: string; password: string; full_name: string; department?: string; role?: string }): Promise<AuthResponse> => {
    const res = await api.post<AuthResponse>('/auth/register', data);
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await api.get<User>('/auth/me');
    return res.data;
  },
};

export const metadataService = {
  getDepartments: async (): Promise<Department[]> => {
    const res = await api.get<Department[]>('/departments');
    return res.data;
  },
  getCategories: async (): Promise<IncidentCategory[]> => {
    const res = await api.get<IncidentCategory[]>('/categories');
    return res.data;
  },
};

export const incidentService = {
  list: async (params?: {
    status?: string;
    severity?: string;
    category_id?: number;
    building?: string;
    department_id?: number;
    search?: string;
    mine_only?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<{ total: number; page: number; page_size: number; incidents: Incident[] }> => {
    const res = await api.get('/incidents', { params });
    return res.data;
  },
  getById: async (id: number): Promise<Incident> => {
    const res = await api.get<Incident>(`/incidents/${id}`);
    return res.data;
  },
  create: async (data: {
    title: string;
    description: string;
    location: string;
    building: string;
    floor_room?: string;
    category_id?: number;
    is_anonymous?: boolean;
    photo_url?: string;
  }): Promise<Incident> => {
    const res = await api.post<Incident>('/incidents', data);
    return res.data;
  },
  previewAI: async (data: {
    title: string;
    description: string;
    location?: string;
    building?: string;
  }) => {
    const res = await api.post('/incidents/ai-preview', data);
    return res.data;
  },
  update: async (id: number, data: Partial<Incident>): Promise<Incident> => {
    const res = await api.patch<Incident>(`/incidents/${id}`, data);
    return res.data;
  },
  updateStatus: async (id: number, status: string, notes?: string): Promise<Incident> => {
    const res = await api.post<Incident>(`/incidents/${id}/status`, { status, notes });
    return res.data;
  },
  assign: async (id: number, department_id: number, notes?: string): Promise<Incident> => {
    const res = await api.post<Incident>(`/incidents/${id}/assign`, { department_id, notes });
    return res.data;
  },
  linkDuplicate: async (id: number, target_incident_id: number, similarity_score?: number, notes?: string) => {
    const res = await api.post(`/incidents/${id}/link-duplicate`, {
      target_incident_id,
      similarity_score,
      notes,
    });
    return res.data;
  },
};

export const analyticsService = {
  getOverview: async (): Promise<StatsOverview> => {
    const res = await api.get<StatsOverview>('/analytics/overview');
    return res.data;
  },
  getHotspots: async (): Promise<HotspotDashboardData> => {
    const res = await api.get<HotspotDashboardData>('/analytics/hotspots');
    return res.data;
  },
};

export const intelligenceService = {
  getPatterns: async (): Promise<DiscoveredPattern[]> => {
    const res = await api.get<DiscoveredPattern[]>('/intelligence/patterns');
    return res.data;
  },
  refreshPatterns: async () => {
    const res = await api.post('/intelligence/patterns/refresh');
    return res.data;
  },
  getRecommendations: async (): Promise<Recommendation[]> => {
    const res = await api.get<Recommendation[]>('/intelligence/recommendations');
    return res.data;
  },
  actionRecommendation: async (id: number, status: 'actioned' | 'dismissed') => {
    const res = await api.post(`/intelligence/recommendations/${id}/action`, { status });
    return res.data;
  },
  queryAssistant: async (query: string): Promise<AssistantResponse> => {
    const res = await api.post<AssistantResponse>('/intelligence/assistant', { query });
    return res.data;
  },
};

export const notificationService = {
  getAll: async (): Promise<NotificationItem[]> => {
    const res = await api.get<NotificationItem[]>('/notifications');
    return res.data;
  },
  markRead: async (id: number) => {
    const res = await api.patch(`/notifications/${id}/read`);
    return res.data;
  },
  markAllRead: async () => {
    const res = await api.post('/notifications/read-all');
    return res.data;
  },
};

export const systemService = {
  getAuditLogs: async (): Promise<AuditLogItem[]> => {
    const res = await api.get<AuditLogItem[]>('/system/audit-logs');
    return res.data;
  },
  seedDemo: async () => {
    const res = await api.post('/system/seed-demo');
    return res.data;
  },
  uploadPhoto: async (file: File): Promise<{ photo_url: string; filename: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/system/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};

export default api;
