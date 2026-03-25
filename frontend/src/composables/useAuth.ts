import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import type { LoginRequest, RegisterRequest } from '@/types/api';

export function useAuth() {
  const authStore = useAuthStore();
  const router = useRouter();

  const isAuthenticated = computed(() => authStore.isAuthenticated);
  const user = computed(() => authStore.user);
  const token = computed(() => authStore.token);

  /**
   * 登录
   */
  const login = async (credentials: LoginRequest): Promise<void> => {
    await authStore.login(credentials);
    // 只有成功后才跳转
    router.push('/');
  };

  /**
   * 注册
   */
  const register = async (data: RegisterRequest): Promise<void> => {
    await authStore.register(data);
    // 只有成功后才跳转
    router.push('/');
  };

  /**
   * 退出登录
   */
  const logout = async (): Promise<void> => {
    try {
      await authStore.logout();
      router.push('/login');
    } catch (error) {
      throw error;
    }
  };

  /**
   * 检查认证状态
   */
  const checkAuth = (): boolean => {
    return authStore.isAuthenticated;
  };

  return {
    isAuthenticated,
    user,
    token,
    login,
    register,
    logout,
    checkAuth
  };
}
