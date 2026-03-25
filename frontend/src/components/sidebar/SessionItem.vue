<template>
  <div 
    class="session-item"
    :class="{ 'session-item--active': isActive }"
    role="listitem"
    @click="handleSelect"
  >
    <div class="session-item__content">
      <div class="session-item__icon">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M2 3C2 2.44772 2.44772 2 3 2H13C13.5523 2 14 2.44772 14 3V10C14 10.5523 13.5523 11 13 11H5L2 14V3Z" 
                stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      
      <div class="session-item__info">
        <div class="session-item__title">
          {{ sessionTitle }}
        </div>
        <div class="session-item__meta">
          <span class="session-item__time">{{ formattedTime }}</span>
          <span v-if="session.messageCount > 0" class="session-item__count">
            {{ session.messageCount }} 条消息
          </span>
        </div>
      </div>
    </div>
    
    <button 
      class="session-item__delete"
      @click.stop="handleDelete"
      aria-label="删除会话"
    >
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Session } from '@/types/chat';

interface Props {
  session: Session;
  isActive: boolean;
}

interface Emits {
  (e: 'select', sessionId: string): void;
  (e: 'delete', sessionId: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const sessionTitle = computed(() => {
  if (props.session.title) {
    return props.session.title;
  }
  
  const firstMessage = props.session.messages[0];
  if (firstMessage && firstMessage.role === 'user') {
    return firstMessage.content.slice(0, 30) + (firstMessage.content.length > 30 ? '...' : '');
  }
  
  return '新会话';
});

const formattedTime = computed(() => {
  const date = new Date(props.session.createdAt);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
});

const handleSelect = () => {
  emit('select', props.session.id);
};

const handleDelete = () => {
  emit('delete', props.session.id);
};
</script>

<style scoped lang="scss">
.session-item {
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 0;
    background: var(--color-primary);
    border-radius: 0 2px 2px 0;
    transition: height var(--transition-fast);
  }
  
  &:hover {
    background-color: var(--color-bg-tertiary);
    border-color: var(--color-border);
    
    .session-item__delete {
      opacity: 1;
    }
  }
  
  &--active {
    background-color: var(--color-bg-tertiary);
    border-color: var(--color-primary);
    
    &::before {
      height: 60%;
    }
    
    .session-item__icon {
      color: var(--color-primary);
    }
    
    .session-item__title {
      color: var(--color-primary);
      font-weight: var(--font-semibold);
    }
    
    .session-item__count {
      background-color: var(--color-primary);
      color: white;
    }
  }
  
  &__content {
    flex: 1;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    min-width: 0;
  }
  
  &__icon {
    flex-shrink: 0;
    color: var(--color-text-secondary);
    transition: color var(--transition-fast);
  }
  
  &__info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  
  &__title {
    font-size: var(--text-sm);
    color: var(--color-text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: all var(--transition-fast);
    line-height: 1.4;
  }
  
  &__meta {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-size: var(--text-xs);
    color: var(--color-text-tertiary);
  }
  
  &__time {
    flex-shrink: 0;
  }
  
  &__count {
    flex-shrink: 0;
    padding: 2px 6px;
    background-color: var(--color-bg-primary);
    border-radius: var(--radius-sm);
    font-size: 10px;
    font-weight: var(--font-medium);
  }
  
  &__delete {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: none;
    color: var(--color-text-secondary);
    cursor: pointer;
    opacity: 0;
    transition: all var(--transition-fast);
    border-radius: var(--radius-sm);
    
    &:hover {
      background-color: var(--color-danger-light);
      color: var(--color-danger);
    }
  }
}
</style>
