<template>
  <aside 
    class="sidebar" 
    :class="{ 'sidebar--collapsed': isCollapsed }"
    role="navigation"
    aria-label="会话导航"
  >
    <div class="sidebar__header">
      <button 
        class="sidebar__toggle"
        @click="toggleSidebar"
        aria-label="切换侧边栏"
      >
        <svg v-if="!isCollapsed" width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M15 5L10 10L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M5 5L10 10L5 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
      
      <h2 v-if="!isCollapsed" class="sidebar__title">医疗问答</h2>
    </div>
    
    <div v-if="!isCollapsed" class="sidebar__content">
      <button 
        class="sidebar__new-session"
        @click="createNewSession"
        aria-label="新建会话"
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M10 5V15M5 10H15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <span>新建会话</span>
      </button>
      
      <div v-if="sessionCount > 0" class="sidebar__session-header">
        <span class="session-header__title">历史对话</span>
        <span class="session-header__count">{{ sessionCount }}</span>
      </div>
      
      <SessionList />
    </div>
    
    <div v-if="!isCollapsed && authStore.isAuthenticated" class="sidebar__footer">
      <div class="sidebar__user">
        <div class="user-avatar">
          {{ userInitial }}
        </div>
        <div class="user-info">
          <div class="user-name">{{ authStore.user?.username }}</div>
          <button 
            class="user-logout"
            @click="handleLogout"
            aria-label="退出登录"
          >
            退出
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useChatStore } from '@/stores/chat';
import SessionList from './SessionList.vue';

const authStore = useAuthStore();
const chatStore = useChatStore();

const isCollapsed = ref(false);

const userInitial = computed(() => {
  const username = authStore.user?.username || 'U';
  return username.charAt(0).toUpperCase();
});

const sessionCount = computed(() => {
  return chatStore.sessions.size;
});

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
};

const createNewSession = () => {
  chatStore.createSession();
};

const handleLogout = async () => {
  await authStore.logout();
};

const loadServerSessionsIfNeeded = async () => {
  if (!authStore.isAuthenticated) return;
  try {
    await chatStore.loadSessionsFromServer();
  } catch (e) {
    console.warn('加载历史会话失败:', e);
    if (chatStore.sessions.size === 0) {
      chatStore.createSession();
    }
  }
};

onMounted(() => {
  loadServerSessionsIfNeeded();
});

watch(
  () => authStore.isAuthenticated,
  (authed) => {
    if (authed) {
      loadServerSessionsIfNeeded();
    }
  }
);
</script>

<style scoped lang="scss">
.sidebar {
  width: 280px;
  height: 100vh;
  background: linear-gradient(180deg, var(--color-bg-primary) 0%, var(--color-bg-secondary) 100%);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  
  &--collapsed {
    width: 60px;
  }
  
  &__header {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
  }
  
  &__toggle {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: transparent;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    color: var(--color-text-secondary);
    cursor: pointer;
    transition: all var(--transition-fast);
    
    &:hover {
      background-color: var(--color-bg-tertiary);
      color: var(--color-primary);
      border-color: var(--color-primary);
    }
  }
  
  &__title {
    font-size: var(--text-lg);
    font-weight: var(--font-bold);
    color: var(--color-text-primary);
    margin: 0;
  }
  
  &__content {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-md);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    
    &::-webkit-scrollbar {
      width: 6px;
    }
    
    &::-webkit-scrollbar-track {
      background: transparent;
    }
    
    &::-webkit-scrollbar-thumb {
      background: var(--color-border);
      border-radius: var(--radius-full);
      
      &:hover {
        background: var(--color-text-tertiary);
      }
    }
  }
  
  &__session-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--spacing-sm);
    margin-top: var(--spacing-sm);
    
    .session-header__title {
      font-size: var(--text-xs);
      font-weight: var(--font-semibold);
      color: var(--color-text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .session-header__count {
      font-size: var(--text-xs);
      font-weight: var(--font-medium);
      color: var(--color-text-tertiary);
      padding: 2px 8px;
      background-color: var(--color-bg-tertiary);
      border-radius: var(--radius-full);
    }
  }
  
  &__new-session {
    width: 100%;
    padding: var(--spacing-md);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
    color: white;
    border: none;
    border-radius: var(--radius-lg);
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    cursor: pointer;
    transition: all var(--transition-fast);
    box-shadow: var(--shadow-sm);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }
    
    &:active {
      transform: translateY(0);
    }
  }
  
  &__footer {
    padding: var(--spacing-lg);
    border-top: 1px solid var(--color-border);
  }
  
  &__user {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    
    .user-avatar {
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
      color: white;
      border-radius: var(--radius-full);
      font-weight: var(--font-bold);
      font-size: var(--text-base);
    }
    
    .user-info {
      flex: 1;
      
      .user-name {
        font-size: var(--text-sm);
        font-weight: var(--font-medium);
        color: var(--color-text-primary);
        margin-bottom: var(--spacing-xs);
      }
      
      .user-logout {
        font-size: var(--text-xs);
        color: var(--color-text-secondary);
        background: none;
        border: none;
        padding: 0;
        cursor: pointer;
        transition: color var(--transition-fast);
        
        &:hover {
          color: var(--color-danger);
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 1000;
    transform: translateX(0);
    
    &--collapsed {
      transform: translateX(-100%);
    }
  }
}
</style>
