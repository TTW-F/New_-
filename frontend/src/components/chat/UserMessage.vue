<template>
  <div class="user-message">
    <div class="user-message__avatar">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="8" r="4" stroke="currentColor" stroke-width="2"/>
        <path d="M6 21C6 17.134 8.686 14 12 14C15.314 14 18 17.134 18 21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </div>
    
    <div class="user-message__content">
      <div class="user-message__text">{{ message.content }}</div>
      <div class="user-message__time">{{ formattedTime }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Message } from '@/types/chat';
import { formatRelativeTime } from '@/utils/format';

interface Props {
  message: Message;
}

const props = defineProps<Props>();

const formattedTime = computed(() => {
  return formatRelativeTime(props.message.timestamp);
});
</script>

<style scoped lang="scss">
.user-message {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  justify-content: flex-end;
  animation: slideInRight var(--transition-normal);
  
  &__avatar {
    order: 2;
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
    color: white;
    border-radius: var(--radius-full);
  }
  
  &__content {
    order: 1;
    max-width: 600px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: var(--spacing-xs);
  }
  
  &__text {
    padding: var(--spacing-md) var(--spacing-lg);
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
    color: white;
    border-radius: var(--radius-lg) var(--radius-lg) var(--radius-sm) var(--radius-lg);
    font-size: var(--text-base);
    line-height: var(--leading-relaxed);
    word-wrap: break-word;
    box-shadow: var(--shadow-sm);
  }
  
  &__time {
    font-size: var(--text-xs);
    color: var(--color-text-secondary);
    padding: 0 var(--spacing-sm);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@media (max-width: 768px) {
  .user-message {
    &__content {
      max-width: 90%;
    }
  }
}
</style>
