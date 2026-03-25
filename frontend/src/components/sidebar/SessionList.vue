<template>
  <div class="session-list" role="list" aria-label="会话列表">
    <div v-if="sessionArray.length === 0" class="session-list__empty">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
          <circle cx="24" cy="24" r="20" stroke="currentColor" stroke-width="2" opacity="0.2"/>
          <path d="M14 18C14 16.8954 14.8954 16 16 16H32C33.1046 16 34 16.8954 34 18V28C34 29.1046 33.1046 30 32 30H20L14 36V18Z" 
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="20" cy="23" r="1.5" fill="currentColor"/>
          <circle cx="24" cy="23" r="1.5" fill="currentColor"/>
          <circle cx="28" cy="23" r="1.5" fill="currentColor"/>
        </svg>
      </div>
      <p class="empty-text">暂无会话记录</p>
      <p class="empty-hint">点击上方按钮开始新的对话</p>
    </div>
    
    <TransitionGroup name="session-list" tag="div" class="session-list__items">
      <SessionItem
        v-for="session in sessionArray"
        :key="session.id"
        :session="session"
        :is-active="session.id === currentSessionId"
        @select="handleSelectSession"
        @delete="handleDeleteSession"
      />
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useChatStore } from '@/stores/chat';
import { useConfirm } from '@/composables/useConfirm';
import SessionItem from './SessionItem.vue';

const chatStore = useChatStore();
const { confirm } = useConfirm();

const sessionArray = computed(() => Array.from(chatStore.sessions.values()));
const currentSessionId = computed(() => chatStore.currentSessionId);

const handleSelectSession = (sessionId: string) => {
  chatStore.switchSession(sessionId);
};

const handleDeleteSession = async (sessionId: string) => {
  const session = chatStore.sessions.get(sessionId);
  const sessionTitle = session?.title || '此会话';
  
  const confirmed = await confirm({
    title: '删除会话',
    message: `确定要删除"${sessionTitle}"吗？`,
    description: '删除后将无法恢复',
    type: 'danger',
    confirmText: '删除',
    cancelText: '取消'
  });
  
  if (confirmed) {
    chatStore.deleteSessionById(sessionId);
  }
};
</script>

<style scoped lang="scss">
.session-list {
  &__empty {
    padding: var(--spacing-2xl) var(--spacing-lg);
    text-align: center;
    color: var(--color-text-secondary);
    
    .empty-icon {
      display: flex;
      justify-content: center;
      margin-bottom: var(--spacing-lg);
      color: var(--color-text-tertiary);
      animation: float 3s ease-in-out infinite;
    }
    
    .empty-text {
      margin: 0 0 var(--spacing-xs) 0;
      font-size: var(--text-base);
      font-weight: var(--font-medium);
      color: var(--color-text-primary);
    }
    
    .empty-hint {
      margin: 0;
      font-size: var(--text-xs);
      color: var(--color-text-tertiary);
      line-height: var(--leading-relaxed);
    }
  }
  
  &__items {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.session-list-enter-active,
.session-list-leave-active {
  transition: all var(--transition-normal);
}

.session-list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.session-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.session-list-move {
  transition: transform var(--transition-normal);
}
</style>
