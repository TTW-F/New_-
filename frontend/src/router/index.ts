import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/HistoryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('@/views/KnowledgeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.meta.requiresAuth;
  const requiresAdmin = to.meta.requiresAdmin;

  // 刷新后仅有 token：尝试恢复 user 信息
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchMe();
    } catch {
      // token 无效则按未登录处理（拦截器会清 token 并跳转）
    }
  }

  if (requiresAuth && !authStore.isAuthenticated) {
    // 需要认证但未登录,跳转到登录页
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if (requiresAdmin && authStore.user?.user_type !== 'admin') {
    // 需要管理员权限但不是管理员
    next({ name: 'Home' });
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    // 已登录用户访问登录页,跳转到首页
    next({ name: 'Home' });
  } else {
    next();
  }
});

export default router;
