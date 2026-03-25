<template>
  <div ref="messageListRef" class="message-list" role="log" aria-live="polite">
    <div v-if="messages.length === 0" class="message-list__empty">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
          <circle cx="32" cy="32" r="28" stroke="currentColor" stroke-width="2" opacity="0.2"/>
          <path d="M20 28C20 28 24 22 32 22C40 22 44 28 44 28M20 36C20 36 24 42 32 42C40 42 44 36 44 36" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <p class="empty-text">开始您的医疗咨询</p>
      <p class="empty-hint">输入您的问题,AI 助手将为您提供专业的医疗建议</p>
    </div>
    
    <TransitionGroup name="message-list" tag="div" class="message-list__items">
      <MessageItem
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :is-streaming="isStreaming && message.id === messages[messages.length - 1]?.id"
      />
    </TransitionGroup>
    
    <div v-if="isStreaming" class="message-list__streaming-indicator">
      <div class="streaming-avatar">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" opacity="0.3"/>
          <path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <span>AI 正在思考</span>
      <TypingIndicator />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue';
import { useChatStore } from '@/stores/chat';
import MessageItem from './MessageItem.vue';
import TypingIndicator from './TypingIndicator.vue';

const chatStore = useChatStore();
const messageListRef = ref<HTMLElement | null>(null);

const messages = computed(() => chatStore.currentMessages);
const isStreaming = computed(() => chatStore.isStreaming);

/**
 * 滚动到底部
 */
const scrollToBottom = (smooth: boolean = true) => {
  if (!messageListRef.value) return;
  
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTo({
        top: messageListRef.value.scrollHeight,
        behavior: smooth ? 'smooth' : 'auto'
      });
    }
  });
};

// 监听消息变化,自动滚动到底部
watch(
  () => messages.value.length,
  () => {
    scrollToBottom();
  }
);

// 监听流式输出状态,自动滚动
watch(
  () => isStreaming.value,
  (newValue) => {
    if (newValue) {
      scrollToBottom();
    }
  }
);

// 监听最后一条消息的内容变化(流式输出时)
watch(
  () => {
    const lastMessage = messages.value[messages.value.length - 1];
    return lastMessage?.content;
  },
  () => {
    // 流式输出时持续滚动
    if (isStreaming.value) {
      scrollToBottom(false);
    }
  }
);
</script>

<style scoped lang="scss">
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
  scroll-behavior: smooth;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--color-bg-secondary);
    border-radius: var(--radius-full);
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--color-border);
    border-radius: var(--radius-full);
    
    &:hover {
      background: var(--color-text-secondary);
    }
  }
  
  &__empty {
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: var(--spacing-2xl);
    
    .empty-icon {
      color: var(--color-text-secondary);
      opacity: 0.5;
      margin-bottom: var(--spacing-lg);
      animation: float 3s ease-in-out infinite;
    }
    
    .empty-text {
      font-size: var(--text-lg);
      font-weight: var(--font-semibold);
      color: var(--color-text-primary);
      margin: 0 0 var(--spacing-sm) 0;
    }
    
    .empty-hint {
      font-size: var(--text-sm);
      color: var(--color-text-secondary);
      margin: 0;
      max-width: 400px;
    }
  }
  
  &__items {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  &__streaming-indicator {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-md) var(--spacing-lg);
    margin-top: var(--spacing-md);
    margin-left: var(--spacing-lg);
    background-color: var(--color-bg-secondary);
    border-radius: var(--radius-lg);
    color: var(--color-text-secondary);
    font-size: var(--text-sm);
    width: fit-content;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--color-border);
    animation: slideInUp 0.3s ease-out;
    
    .streaming-avatar {
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--color-primary);
      animation: pulse 2s ease-in-out infinite;
    }
  }
}

.message-list-enter-active {
  transition: all var(--transition-normal);
}

.message-list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style>
