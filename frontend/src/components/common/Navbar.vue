<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-brand" @click="goHome">
        <svg class="brand-icon" width="32" height="32" viewBox="0 0 32 32" fill="none">
          <rect width="32" height="32" rx="8" fill="url(#brand-gradient)"/>
          <path d="M16 10V22M10 16H22" stroke="white" stroke-width="2" stroke-linecap="round"/>
          <defs>
            <linearGradient id="brand-gradient" x1="0" y1="0" x2="32" y2="32">
              <stop offset="0%" stop-color="#3B82F6"/>
              <stop offset="100%" stop-color="#8B5CF6"/>
            </linearGradient>
          </defs>
        </svg>
        <span class="brand-text">医疗问答系统</span>
      </div>

      <div class="navbar-menu">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          <component :is="item.icon" class="nav-icon" />
          <span class="nav-text">{{ item.label }}</span>
        </router-link>
      </div>

      <div class="navbar-user">
        <div class="user-info" @click="toggleDropdown">
          <div class="user-avatar">
            {{ userInitial }}
          </div>
          <span class="user-name">{{ authStore.user?.username }}</span>
          <span class="dropdown-arrow">▼</span>
        </div>

        <div v-if="showDropdown" class="user-dropdown">
          <div class="dropdown-item" @click="goToProfile">
            <svg class="item-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>个人中心</span>
          </div>
          <div v-if="isAdmin" class="dropdown-item" @click="goToAdmin">
            <svg class="item-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>系统管理</span>
          </div>
          <div class="dropdown-divider"></div>
          <div class="dropdown-item logout" @click="handleLogout">
            <svg class="item-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>退出登录</span>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, h } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useToast } from '@/composables/useToast';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { showToast } = useToast();

const showDropdown = ref(false);

// SVG图标组件
const HomeIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
  h('path', { d: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
]);

const ChatIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
  h('path', { d: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
]);

const HistoryIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
  h('path', { d: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
]);

const KnowledgeIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
  h('path', { d: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
]);

const AdminIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor' }, [
  h('path', { d: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }),
  h('path', { d: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' })
]);

const isAdmin = computed(() => {
  return authStore.user?.user_type === 'admin';
});

const menuItems = computed(() => {
  const items = [
    { path: '/', label: '首页', icon: HomeIcon },
    { path: '/chat', label: '智能问答', icon: ChatIcon },
    { path: '/history', label: '历史记录', icon: HistoryIcon },
    { path: '/knowledge', label: '知识库', icon: KnowledgeIcon }
  ];
  
  // 如果是管理员，添加后台管理入口
  if (isAdmin.value) {
    items.push({ path: '/admin', label: '系统管理', icon: AdminIcon });
  }
  
  return items;
});

const userInitial = computed(() => {
  return authStore.user?.username?.charAt(0).toUpperCase() || 'U';
});

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/';
  }
  return route.path.startsWith(path);
};

const goHome = () => {
  router.push('/');
};

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

const goToProfile = () => {
  showDropdown.value = false;
  router.push('/profile');
};

const goToAdmin = () => {
  showDropdown.value = false;
  router.push('/admin');
};

const handleLogout = async () => {
  showDropdown.value = false;
  await authStore.logout();
  router.push('/login');
  showToast('已退出登录', 'success');
};

// 点击外部关闭下拉菜单
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement;
  if (!target.closest('.navbar-user')) {
    showDropdown.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped lang="scss">
.navbar {
  background: var(--color-bg-primary);
  box-shadow: var(--shadow-md);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: var(--z-dropdown);
}

.navbar-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    opacity: 0.8;
  }

  .brand-icon {
    flex-shrink: 0;
  }

  .brand-text {
    font-size: var(--text-xl);
    font-weight: var(--font-bold);
    color: var(--color-text-primary);
  }
}

.navbar-menu {
  display: flex;
  gap: 8px;
  flex: 1;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
  font-size: var(--text-base);

  .nav-icon {
    flex-shrink: 0;
    display: flex;
    align-items: center;
  }

  &:hover {
    background: var(--color-bg-tertiary);
    color: var(--color-text-primary);
  }

  &.active {
    background: var(--color-primary);
    color: white;
    font-weight: var(--font-semibold);
  }
}

.navbar-user {
  position: relative;

  .user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 16px;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-fast);

    &:hover {
      background: var(--color-bg-tertiary);
    }

    .user-avatar {
      width: 36px;
      height: 36px;
      border-radius: var(--radius-full);
      background: var(--color-primary);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: var(--font-bold);
      font-size: var(--text-base);
    }

    .user-name {
      font-size: var(--text-sm);
      color: var(--color-text-primary);
      font-weight: var(--font-medium);
    }

    .dropdown-arrow {
      font-size: 10px;
      color: var(--color-text-tertiary);
      transition: transform var(--transition-fast);
    }
  }

  .user-dropdown {
    position: absolute;
    top: calc(100% + 8px);
    right: 0;
    background: var(--color-bg-primary);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-xl);
    border: 1px solid var(--color-border);
    min-width: 180px;
    overflow: hidden;
    animation: dropdownFadeIn 0.2s ease;

    .dropdown-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      cursor: pointer;
      transition: all var(--transition-fast);
      font-size: var(--text-sm);
      color: var(--color-text-primary);

      .item-icon {
        flex-shrink: 0;
        display: flex;
        align-items: center;
      }

      &:hover {
        background: var(--color-bg-tertiary);
      }

      &.logout {
        color: var(--color-error);

        &:hover {
          background: rgba(239, 68, 68, 0.1);
        }
      }
    }

    .dropdown-divider {
      height: 1px;
      background: var(--color-border);
      margin: 4px 0;
    }
  }
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .navbar-container {
    padding: 0 16px;
  }

  .navbar-brand {
    .brand-text {
      display: none;
    }
  }

  .navbar-menu {
    gap: 4px;
  }

  .nav-item {
    padding: 8px 12px;

    .nav-text {
      display: none;
    }
  }

  .user-info {
    .user-name {
      display: none;
    }
  }
}
</style>
