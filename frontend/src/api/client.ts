// HTTP API 客户端

import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器 - 添加 Token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 处理错误
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const requestUrl: string = error.config?.url || '';
      const isAuthEndpoint =
        requestUrl.includes('/api/v1/auth/login') ||
        requestUrl.includes('/api/v1/auth/register') ||
        requestUrl.includes('/api/v1/auth/login/form');

      // 登录/注册失败属于正常业务错误：交给页面展示，不要全局强制跳转
      if (!isAuthEndpoint) {
        // Token 失效/未登录访问受保护资源：清除 token 并跳转登录
        localStorage.removeItem('access_token');
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
