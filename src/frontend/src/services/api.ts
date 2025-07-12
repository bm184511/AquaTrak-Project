import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';
import {
  ApiResponse,
  ApiError,
  LoginRequest,
  LoginResponse,
  User,
  Module,
  AnalysisResult,
  Alert,
  Dashboard,
  Organization,
  DataFilter,
  PaginatedResponse
} from '../types/api';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30 seconds

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
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

// Response interceptor for handling errors and token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh token failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Handle other errors
    const errorMessage = error.response?.data?.message || error.message || 'An error occurred';
    toast.error(errorMessage);
    
    return Promise.reject(error);
  }
);

// Generic API response handler
const handleApiResponse = <T>(response: AxiosResponse<ApiResponse<T>>): T => {
  if (response.data.status === 'success') {
    return response.data.data;
  }
  throw new Error(response.data.message || 'API request failed');
};

// Generic API error handler
const handleApiError = (error: any): never => {
  if (axios.isAxiosError(error)) {
    const apiError: ApiError = {
      error: error.response?.data?.error || 'API Error',
      message: error.response?.data?.message || error.message,
      details: error.response?.data?.details,
      status_code: error.response?.status || 500,
      timestamp: new Date().toISOString(),
    };
    throw apiError;
  }
  throw error;
};

// Authentication API
export const authAPI = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    try {
      const response = await apiClient.post<ApiResponse<LoginResponse>>('/api/v1/auth/login', credentials);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/api/v1/auth/logout');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    } catch (error) {
      // Even if logout fails, clear local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      return handleApiError(error);
    }
  },

  refreshToken: async (refreshToken: string): Promise<{ access_token: string }> => {
    try {
      const response = await apiClient.post<ApiResponse<{ access_token: string }>>('/api/v1/auth/refresh', {
        refresh_token: refreshToken,
      });
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getProfile: async (): Promise<User> => {
    try {
      const response = await apiClient.get<ApiResponse<User>>('/api/v1/auth/profile');
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    try {
      const response = await apiClient.put<ApiResponse<User>>('/api/v1/auth/profile', userData);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// Modules API
export const modulesAPI = {
  getAll: async (): Promise<Module[]> => {
    try {
      const response = await apiClient.get<ApiResponse<Module[]>>('/api/v1/modules');
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getById: async (moduleId: string): Promise<Module> => {
    try {
      const response = await apiClient.get<ApiResponse<Module>>(`/api/v1/modules/${moduleId}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  updateConfig: async (moduleId: string, config: any): Promise<Module> => {
    try {
      const response = await apiClient.put<ApiResponse<Module>>(`/api/v1/modules/${moduleId}/config`, config);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getStatus: async (moduleId: string): Promise<{ status: string; last_update: string }> => {
    try {
      const response = await apiClient.get<ApiResponse<{ status: string; last_update: string }>>(`/api/v1/modules/${moduleId}/status`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// Analysis API
export const analysisAPI = {
  getAll: async (filters?: DataFilter): Promise<PaginatedResponse<AnalysisResult>> => {
    try {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            if (Array.isArray(value)) {
              value.forEach(v => params.append(key, v));
            } else {
              params.append(key, String(value));
            }
          }
        });
      }

      const response = await apiClient.get<PaginatedResponse<AnalysisResult>>(`/api/v1/analysis?${params.toString()}`);
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  getById: async (analysisId: string): Promise<AnalysisResult> => {
    try {
      const response = await apiClient.get<ApiResponse<AnalysisResult>>(`/api/v1/analysis/${analysisId}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  create: async (moduleId: string, analysisData: any): Promise<AnalysisResult> => {
    try {
      const response = await apiClient.post<ApiResponse<AnalysisResult>>(`/api/v1/modules/${moduleId}/analysis`, analysisData);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  cancel: async (analysisId: string): Promise<void> => {
    try {
      await apiClient.post(`/api/v1/analysis/${analysisId}/cancel`);
    } catch (error) {
      return handleApiError(error);
    }
  },

  delete: async (analysisId: string): Promise<void> => {
    try {
      await apiClient.delete(`/api/v1/analysis/${analysisId}`);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// IoT Water Consumption API
export const iotAPI = {
  getData: async (deviceId?: string, filters?: DataFilter): Promise<any[]> => {
    try {
      const params = new URLSearchParams();
      if (deviceId) params.append('device_id', deviceId);
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, String(value));
          }
        });
      }

      const response = await apiClient.get<ApiResponse<any[]>>(`/api/v1/iot/water-consumption?${params.toString()}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getAnalysis: async (analysisId: string): Promise<any> => {
    try {
      const response = await apiClient.get<ApiResponse<any>>(`/api/v1/iot/analysis/${analysisId}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  runAnalysis: async (parameters: any): Promise<AnalysisResult> => {
    try {
      const response = await apiClient.post<ApiResponse<AnalysisResult>>('/api/v1/iot/analysis', parameters);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// Environmental Health API
export const environmentalHealthAPI = {
  getData: async (filters?: DataFilter): Promise<any[]> => {
    try {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, String(value));
          }
        });
      }

      const response = await apiClient.get<ApiResponse<any[]>>(`/api/v1/environmental-health?${params.toString()}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getAnalysis: async (analysisId: string): Promise<any> => {
    try {
      const response = await apiClient.get<ApiResponse<any>>(`/api/v1/environmental-health/analysis/${analysisId}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  runAnalysis: async (parameters: any): Promise<AnalysisResult> => {
    try {
      const response = await apiClient.post<ApiResponse<AnalysisResult>>('/api/v1/environmental-health/analysis', parameters);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// Urban Green Space API
export const greenSpaceAPI = {
  getData: async (filters?: DataFilter): Promise<any[]> => {
    try {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, String(value));
          }
        });
      }

      const response = await apiClient.get<ApiResponse<any[]>>(`/api/v1/urban-green-space?${params.toString()}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getAnalysis: async (analysisId: string): Promise<any> => {
    try {
      const response = await apiClient.get<ApiResponse<any>>(`/api/v1/urban-green-space/analysis/${analysisId}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  runAnalysis: async (parameters: any): Promise<AnalysisResult> => {
    try {
      const response = await apiClient.post<ApiResponse<AnalysisResult>>('/api/v1/urban-green-space/analysis', parameters);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// Urban Water Network API
export const waterNetworkAPI = {
  getData: async (networkId?: string, filters?: DataFilter): Promise<any[]> => {
    try {
      const params = new URLSearchParams();
      if (networkId) params.append('network_id', networkId);
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, String(value));
          }
        });
      }

      const response = await apiClient.get<ApiResponse<any[]>>(`/api/v1/urban-water-network?${params.toString()}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getAnalysis: async (analysisId: string): Promise<any> => {
    try {
      const response = await apiClient.get<ApiResponse<any>>(`/api/v1/urban-water-network/analysis/${analysisId}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  runAnalysis: async (parameters: any): Promise<AnalysisResult> => {
    try {
      const response = await apiClient.post<ApiResponse<AnalysisResult>>('/api/v1/urban-water-network/analysis', parameters);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// Alerts API
export const alertsAPI = {
  getAll: async (filters?: DataFilter): Promise<PaginatedResponse<Alert>> => {
    try {
      const params = new URLSearchParams();
      if (filters) {
        Object.entries(filters).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            if (Array.isArray(value)) {
              value.forEach(v => params.append(key, v));
            } else {
              params.append(key, String(value));
            }
          }
        });
      }

      const response = await apiClient.get<PaginatedResponse<Alert>>(`/api/v1/alerts?${params.toString()}`);
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  getById: async (alertId: string): Promise<Alert> => {
    try {
      const response = await apiClient.get<ApiResponse<Alert>>(`/api/v1/alerts/${alertId}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  acknowledge: async (alertId: string): Promise<Alert> => {
    try {
      const response = await apiClient.post<ApiResponse<Alert>>(`/api/v1/alerts/${alertId}/acknowledge`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  resolve: async (alertId: string): Promise<Alert> => {
    try {
      const response = await apiClient.post<ApiResponse<Alert>>(`/api/v1/alerts/${alertId}/resolve`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  dismiss: async (alertId: string): Promise<Alert> => {
    try {
      const response = await apiClient.post<ApiResponse<Alert>>(`/api/v1/alerts/${alertId}/dismiss`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// Dashboards API
export const dashboardsAPI = {
  getAll: async (): Promise<Dashboard[]> => {
    try {
      const response = await apiClient.get<ApiResponse<Dashboard[]>>('/api/v1/dashboards');
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getById: async (dashboardId: string): Promise<Dashboard> => {
    try {
      const response = await apiClient.get<ApiResponse<Dashboard>>(`/api/v1/dashboards/${dashboardId}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  create: async (dashboardData: Partial<Dashboard>): Promise<Dashboard> => {
    try {
      const response = await apiClient.post<ApiResponse<Dashboard>>('/api/v1/dashboards', dashboardData);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  update: async (dashboardId: string, dashboardData: Partial<Dashboard>): Promise<Dashboard> => {
    try {
      const response = await apiClient.put<ApiResponse<Dashboard>>(`/api/v1/dashboards/${dashboardId}`, dashboardData);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  delete: async (dashboardId: string): Promise<void> => {
    try {
      await apiClient.delete(`/api/v1/dashboards/${dashboardId}`);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// Organizations API
export const organizationsAPI = {
  getCurrent: async (): Promise<Organization> => {
    try {
      const response = await apiClient.get<ApiResponse<Organization>>('/api/v1/organizations/current');
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  update: async (organizationData: Partial<Organization>): Promise<Organization> => {
    try {
      const response = await apiClient.put<ApiResponse<Organization>>('/api/v1/organizations/current', organizationData);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// System API
export const systemAPI = {
  health: async (): Promise<any> => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },

  dbInfo: async (): Promise<any> => {
    try {
      const response = await apiClient.get('/db/info');
      return response.data;
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// Admin API
export const adminAPI = {
  // Dashboard
  getDashboard: async () => {
    try {
      const response = await apiClient.get<ApiResponse<any>>('/api/v1/admin/dashboard');
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // User Management
  getUsers: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    role?: string;
    status?: string;
    country?: string;
  }) => {
    try {
      const response = await apiClient.get<ApiResponse<any>>('/api/v1/admin/users', { params });
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getUser: async (userId: string) => {
    try {
      const response = await apiClient.get<ApiResponse<any>>(`/api/v1/admin/users/${userId}`);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  createUser: async (userData: any) => {
    try {
      const response = await apiClient.post<ApiResponse<any>>('/api/v1/admin/users', userData);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  updateUser: async (userId: string, userData: any) => {
    try {
      const response = await apiClient.put<ApiResponse<any>>(`/api/v1/admin/users/${userId}`, userData);
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  deleteUser: async (userId: string) => {
    try {
      await apiClient.delete(`/api/v1/admin/users/${userId}`);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Organization Management
  getOrganizations: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    type?: string;
    country?: string;
  }) => {
    try {
      const response = await apiClient.get<ApiResponse<any>>('/api/v1/admin/organizations', { params });
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // System Monitoring
  getSystemStatus: async () => {
    try {
      const response = await apiClient.get<ApiResponse<any>>('/api/v1/admin/system/status');
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getSystemPerformance: async () => {
    try {
      const response = await apiClient.get<ApiResponse<any>>('/api/v1/admin/system/performance');
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getSystemLogs: async (params?: {
    page?: number;
    limit?: number;
    level?: string;
    user_id?: string;
    action?: string;
  }) => {
    try {
      const response = await apiClient.get<ApiResponse<any>>('/api/v1/admin/system/logs', { params });
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Data Management
  getDataSources: async () => {
    try {
      const response = await apiClient.get<ApiResponse<any>>('/api/v1/admin/data/sources');
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getFileUploads: async (params?: {
    page?: number;
    limit?: number;
    status?: string;
    user_id?: string;
  }) => {
    try {
      const response = await apiClient.get<ApiResponse<any>>('/api/v1/admin/data/uploads', { params });
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  // Analytics
  getUsageAnalytics: async (params?: { period?: string }) => {
    try {
      const response = await apiClient.get<ApiResponse<any>>('/api/v1/admin/analytics/usage', { params });
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },

  getModuleAnalytics: async (params?: { period?: string }) => {
    try {
      const response = await apiClient.get<ApiResponse<any>>('/api/v1/admin/analytics/modules', { params });
      return handleApiResponse(response);
    } catch (error) {
      return handleApiError(error);
    }
  },
};

// Export all API modules
export {
  apiClient,
  handleApiResponse,
  handleApiError,
}; 