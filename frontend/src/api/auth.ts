// 认证 API

import apiClient from './client';
import type { LoginRequest, RegisterRequest, LoginResponse, User } from '@/types/api';

/** 用户登录 */
export async function login(request: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/api/v1/auth/login', request);
  return response.data;
}

/** 用户注册 */
export async function register(request: RegisterRequest): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/api/v1/auth/register', request);
  return response.data;
}

/** 用户登出 */
export async function logout(): Promise<void> {
  await apiClient.post('/api/v1/auth/logout');
}

/** 获取当前用户信息 */
export async function me(): Promise<User> {
  const response = await apiClient.get<User>('/api/v1/auth/me');
  return response.data;
}
