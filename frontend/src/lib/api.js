import axios from 'axios';

// Configuração base da API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Criar instância do axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para lidar com respostas e erros
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Se o token expirou (401) e não é uma tentativa de refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data.tokens;
          
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', newRefreshToken);

          // Repetir a requisição original com o novo token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Se o refresh falhou, redirecionar para login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Funções de autenticação
export const authAPI = {
  login: (email, password) => 
    api.post('/auth/login', { email, password }),
  
  register: (nome, email, password, empresa_nome, empresa_slug) => 
    api.post('/auth/register', { nome, email, password, empresa_nome, empresa_slug }),
  
  refresh: (refresh_token) => 
    api.post('/auth/refresh', { refresh_token }),
  
  me: () => 
    api.get('/auth/me'),
  
  logout: () => 
    api.post('/auth/logout'),
};

// Funções para contatos
export const contatosAPI = {
  getAll: (params = {}) => 
    api.get('/contatos', { params }),
  
  create: (data) => 
    api.post('/contatos', data),
  
  update: (id, data) => 
    api.put(`/contatos/${id}`, data),
  
  delete: (id) => 
    api.delete(`/contatos/${id}`),
  
  import: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/contatos/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  export: () => 
    api.get('/contatos/export', { responseType: 'blob' }),
  
  getStats: () => 
    api.get('/contatos/stats'),
};

// Funções para campanhas
export const campanhasAPI = {
  getAll: () => 
    api.get('/campanhas'),
  
  create: (data) => 
    api.post('/campanhas', data),
  
  update: (id, data) => 
    api.put(`/campanhas/${id}`, data),
  
  execute: (id, data = {}) => 
    api.post(`/campanhas/${id}/execute`, data),
  
  pause: (id) => 
    api.post(`/campanhas/${id}/pause`),
  
  resume: (id) => 
    api.post(`/campanhas/${id}/resume`),
  
  cancel: (id) => 
    api.post(`/campanhas/${id}/cancel`),
  
  getStats: (id) => 
    api.get(`/campanhas/${id}/stats`),
  
  getTemplates: () => 
    api.get('/campanhas/templates'),
};

// Funções para dashboard
export const dashboardAPI = {
  getMetrics: () => 
    api.get('/dashboard/metrics'),
  
  getRecentActivity: () => 
    api.get('/dashboard/recent-activity'),
  
  getDisparosPorDia: (days = 30) => 
    api.get('/dashboard/charts/disparos-por-dia', { params: { days } }),
  
  getRespostasPorSentimento: () => 
    api.get('/dashboard/charts/respostas-por-sentimento'),
  
  getCampanhasPerformance: () => 
    api.get('/dashboard/charts/campanhas-performance'),
  
  exportReport: () => 
    api.get('/dashboard/export/report'),
};

// Health check
export const healthAPI = {
  check: () => 
    api.get('/health'),
};

export default api;

