import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Store de autenticação
export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      
      setAuth: (user, tokens) => set({
        user,
        tokens,
        isAuthenticated: true,
      }),
      
      clearAuth: () => set({
        user: null,
        tokens: null,
        isAuthenticated: false,
      }),
      
      updateUser: (userData) => set((state) => ({
        user: { ...state.user, ...userData },
      })),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Store principal da aplicação
export const useAppStore = create((set, get) => ({
  // Estado de loading global
  isLoading: false,
  setLoading: (loading) => set({ isLoading: loading }),
  
  // Contatos
  contatos: [],
  contatosLoading: false,
  contatosStats: null,
  
  setContatos: (contatos) => set({ contatos }),
  setContatosLoading: (loading) => set({ contatosLoading: loading }),
  setContatosStats: (stats) => set({ contatosStats: stats }),
  
  addContato: (contato) => set((state) => ({
    contatos: [...state.contatos, contato],
  })),
  
  updateContato: (id, updatedContato) => set((state) => ({
    contatos: state.contatos.map(c => 
      c.id === id ? { ...c, ...updatedContato } : c
    ),
  })),
  
  removeContato: (id) => set((state) => ({
    contatos: state.contatos.filter(c => c.id !== id),
  })),
  
  // Campanhas
  campanhas: [],
  campanhasLoading: false,
  activeCampanha: null,
  
  setCampanhas: (campanhas) => set({ campanhas }),
  setCampanhasLoading: (loading) => set({ campanhasLoading: loading }),
  setActiveCampanha: (campanha) => set({ activeCampanha: campanha }),
  
  addCampanha: (campanha) => set((state) => ({
    campanhas: [...state.campanhas, campanha],
  })),
  
  updateCampanha: (id, updatedCampanha) => set((state) => ({
    campanhas: state.campanhas.map(c => 
      c.id === id ? { ...c, ...updatedCampanha } : c
    ),
  })),
  
  // Dashboard
  dashboardMetrics: null,
  dashboardLoading: false,
  recentActivity: [],
  
  setDashboardMetrics: (metrics) => set({ dashboardMetrics: metrics }),
  setDashboardLoading: (loading) => set({ dashboardLoading: loading }),
  setRecentActivity: (activity) => set({ recentActivity: activity }),
  
  // Notificações
  notifications: [],
  
  addNotification: (notification) => set((state) => ({
    notifications: [...state.notifications, {
      id: Date.now(),
      timestamp: new Date(),
      ...notification,
    }],
  })),
  
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter(n => n.id !== id),
  })),
  
  clearNotifications: () => set({ notifications: [] }),
  
  // UI State
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  
  // Filtros e busca
  searchTerm: '',
  setSearchTerm: (term) => set({ searchTerm: term }),
  
  filters: {
    status: 'all',
    tipo: 'all',
    canal: 'all',
  },
  
  setFilter: (key, value) => set((state) => ({
    filters: { ...state.filters, [key]: value },
  })),
  
  clearFilters: () => set({
    filters: {
      status: 'all',
      tipo: 'all',
      canal: 'all',
    },
    searchTerm: '',
  }),
}));

// Hooks personalizados para facilitar o uso
export const useAuth = () => {
  const { user, tokens, isAuthenticated, setAuth, clearAuth, updateUser } = useAuthStore();
  
  const login = (user, tokens) => {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    setAuth(user, tokens);
  };
  
  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    clearAuth();
  };
  
  return {
    user,
    tokens,
    isAuthenticated,
    login,
    logout,
    updateUser,
  };
};

export const useNotifications = () => {
  const { notifications, addNotification, removeNotification, clearNotifications } = useAppStore();
  
  const showSuccess = (message, title = 'Sucesso') => {
    addNotification({
      type: 'success',
      title,
      message,
    });
  };
  
  const showError = (message, title = 'Erro') => {
    addNotification({
      type: 'error',
      title,
      message,
    });
  };
  
  const showWarning = (message, title = 'Atenção') => {
    addNotification({
      type: 'warning',
      title,
      message,
    });
  };
  
  const showInfo = (message, title = 'Informação') => {
    addNotification({
      type: 'info',
      title,
      message,
    });
  };
  
  return {
    notifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeNotification,
    clearNotifications,
  };
};

