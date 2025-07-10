import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginRequest } from '@/types/api';
import { authAPI } from '@/services/api';

interface AuthState {
  // State
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
  setUser: (user: User) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  clearAuth: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (credentials: LoginRequest) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authAPI.login(credentials);
          
          set({
            user: response.user,
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });

          // Store tokens in localStorage for persistence
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('refresh_token', response.refresh_token);
          localStorage.setItem('user', JSON.stringify(response.user));
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.message || 'Login failed',
          });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          await authAPI.logout();
        } catch (error) {
          // Continue with logout even if API call fails
          console.error('Logout API error:', error);
        } finally {
          get().clearAuth();
          set({ isLoading: false });
        }
      },

      refreshAuth: async () => {
        const { refreshToken } = get();
        if (!refreshToken) {
          get().clearAuth();
          return;
        }

        set({ isLoading: true });
        try {
          const response = await authAPI.refreshToken(refreshToken);
          
          set({
            accessToken: response.access_token,
            isLoading: false,
            error: null,
          });

          localStorage.setItem('access_token', response.access_token);
        } catch (error: any) {
          get().clearAuth();
          set({
            isLoading: false,
            error: error.message || 'Token refresh failed',
          });
        }
      },

      setUser: (user: User) => {
        set({ user });
        localStorage.setItem('user', JSON.stringify(user));
      },

      setTokens: (accessToken: string, refreshToken: string) => {
        set({
          accessToken,
          refreshToken,
          isAuthenticated: true,
        });
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
      },

      clearAuth: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
        });
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      setError: (error: string | null) => {
        set({ error });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Selectors for better performance
export const useUser = () => useAuthStore((state) => state.user);
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated);
export const useIsLoading = () => useAuthStore((state) => state.isLoading);
export const useAuthError = () => useAuthStore((state) => state.error);
export const useAccessToken = () => useAuthStore((state) => state.accessToken); 