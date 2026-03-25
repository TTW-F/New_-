<template>
  <div class="chat-container">
    <Sidebar />
    
    <div class="chat-container__main">
      <div class="chat-container__header">
        <button
          class="mobile-menu-toggle"
          @click="toggleSidebar"
          aria-label="切换侧边栏"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M4 6H20M4 12H20M4 18H20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
        
        <h1 class="chat-container__title">
          {{ currentSessionTitle }}
        </h1>
        
        <div class="chat-container__actions">
          <button
            v-if="isStreaming"
            class="action-button action-button--stop"
            @click="stopStreaming"
            aria-label="停止生成"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <rect x="5" y="5" width="10" height="10" rx="1" fill="currentColor"/>
            </svg>
            <span>停止</span>
          </button>
          
          <button
            class="action-button"
            @click="clearSession"
            aria-label="清空会话"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 6H16M6 6V4C6 3.44772 6.44772 3 7 3H13C13.5523 3 14 3.44772 14 4V6M8 9V14M12 9V14M5 6L6 16C6 16.5523 6.44772 17 7 17H13C13.5523 17 14 16.5523 14 16L15 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>
      
      <MessageList />
      
      <InputBox @submit="handleSendMessage" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useChatStore } from '@/stores/chat';
import { useChat } from '@/composables/useChat';
import { useConfirm } from '@/composables/useConfirm';
import { useToast } from '@/composables/useToast';
import Sidebar from '@/components/sidebar/Sidebar.vue';
import MessageList from './MessageList.vue';
import InputBox from './InputBox.vue';

const chatStore = useChatStore();
const { sendMessage, stopStreaming } = useChat();
const { confirm } = useConfirm();
const { error: showError } = useToast();

const isStreaming = computed(() => chatStore.isStreaming);

const currentSessionTitle = computed(() => {
  const session = chatStore.currentSession;
  if (!session) return '新会话';
  
  if (session.title) return session.title;
  
  const firstMessage = session.messages[0];
  if (firstMessage && firstMessage.role === 'user') {
    return firstMessage.content.slice(0, 30) + (firstMessage.content.length > 30 ? '...' : '');
  }
  
  return '新会话';
});

const handleSendMessage = async (content: string) => {
  try {
    await sendMessage(content);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '发送消息失败';
    showError(errorMessage);
  }
};

const toggleSidebar = () => {
  // 移动端侧边栏切换逻辑
  const sidebar = document.querySelector('.sidebar');
  sidebar?.classList.toggle('sidebar--collapsed');
};

const clearSession = async () => {
  const confirmed = await confirm({
    title: '清空会话',
    message: '确定要清空当前会话吗?',
    description: '此操作将删除所有消息记录,且无法恢复',
    type: 'warning',
    confirmText: '清空',
    cancelText: '取消'
  });
  
  if (confirmed) {
    chatStore.clearCurrentSession();
  }
};
</script>

<style scoped lang="scss">
.chat-container {
  display: flex;
  height: 100vh;
  background-color: var(--color-bg-secondary);
  
  &__main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  
  &__header {
    height: 56px;
    padding: 0 var(--spacing-lg);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    background-color: var(--color-bg-primary);
    border-bottom: 1px solid var(--color-border);
    
    .mobile-menu-toggle {
      display: none;
      width: 40px;
      height: 40px;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      color: var(--color-text-secondary);
      cursor: pointer;
      border-radius: var(--radius-md);
      transition: all var(--transition-fast);
      
      &:hover {
        background-color: var(--color-bg-tertiary);
        color: var(--color-text-primary);
      }
    }
  }
  
  &__title {
    flex: 1;
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: var(--color-text-primary);
    margin: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  &__actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    
    .action-button {
      display: flex;
      align-items: center;
      gap: var(--spacing-xs);
      padding: var(--spacing-sm) var(--spacing-md);
      background: none;
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      color: var(--color-text-secondary);
      font-size: var(--text-sm);
      cursor: pointer;
      transition: all var(--transition-fast);
      
      &:hover {
        background-color: var(--color-bg-tertiary);
        color: var(--color-text-primary);
        border-color: var(--color-text-secondary);
      }
      
      &--stop {
        color: var(--color-danger);
        border-color: var(--color-danger);
        
        &:hover {
          background-color: var(--color-danger-light);
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .chat-container {
    &__header {
      .mobile-menu-toggle {
        display: flex;
      }
    }
    
    &__actions {
      .action-button span {
        display: none;
      }
    }
  }
}
</style>
