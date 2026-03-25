// Auth Store - 认证状态管理

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User, LoginRequest, RegisterRequest } from '@/types/api';
import * as authAPI from '@/api/auth';

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'));
  const user = ref<User | null>(null);
  
  const isAuthenticated = computed(() => !!token.value);
  
  function setToken(newToken: string): void {
    token.value = newToken;
    localStorage.setItem('access_token', newToken);
  }
  
  function setUser(newUser: User): void {
    user.value = newUser;
  }
  
  function clearAuth(): void {
    token.value = null;
    user.value = null;
    localStorage.removeItem('access_token');
  }
  
  async function login(credentials: LoginRequest): Promise<void> {
    const response = await authAPI.login(credentials);
    setToken(response.access_token);
    setUser(response.user);
  }
  
  async function register(data: RegisterRequest): Promise<void> {
    const response = await authAPI.register(data);
    setToken(response.access_token);
    setUser(response.user);
  }
  
  async function logout(): Promise<void> {
    try {
      await authAPI.logout();
    } finally {
      clearAuth();
    }
  }

  async function fetchMe(): Promise<void> {
    if (!token.value) return;
    const me = await authAPI.me();
    setUser(me);
  }
  
  return {
    token,
    user,
    isAuthenticated,
    setToken,
    setUser,
    clearAuth,
    fetchMe,
    login,
    register,
    logout
  };
});
