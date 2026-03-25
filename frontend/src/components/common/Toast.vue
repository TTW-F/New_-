<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast"
          :class="`toast--${toast.type}`"
          role="alert"
          @click="removeToast(toast.id)"
        >
          <div class="toast__icon">
            <svg v-if="toast.type === 'success'" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M16.6667 5L7.50004 14.1667L3.33337 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else-if="toast.type === 'error'" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <svg v-else-if="toast.type === 'warning'" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 6V11M10 14H10.01M18 10C18 14.4183 14.4183 18 10 18C5.58172 18 2 14.4183 2 10C2 5.58172 5.58172 2 10 2C14.4183 2 18 5.58172 18 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 11V6M10 14H10.01M18 10C18 14.4183 14.4183 18 10 18C5.58172 18 2 14.4183 2 10C2 5.58172 5.58172 2 10 2C14.4183 2 18 5.58172 18 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          
          <div class="toast__message">{{ toast.message }}</div>
          
          <button 
            class="toast__close"
            @click.stop="removeToast(toast.id)"
            aria-label="关闭"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast } from '@/composables/useToast';

const { toasts, removeToast } = useToast();
</script>

<style scoped lang="scss">
.toast-container {
  position: fixed;
  top: var(--spacing-lg);
  right: var(--spacing-lg);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  pointer-events: none;
}

.toast {
  min-width: 300px;
  max-width: 500px;
  padding: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  pointer-events: auto;
  cursor: pointer;
  
  &__icon {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  &__message {
    flex: 1;
    font-size: var(--text-sm);
    line-height: var(--leading-normal);
  }
  
  &__close {
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
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
    
    &:hover {
      background-color: rgba(0, 0, 0, 0.05);
    }
  }
  
  &--success {
    border-left: 4px solid var(--color-success);
    
    .toast__icon {
      color: var(--color-success);
    }
  }
  
  &--error {
    border-left: 4px solid var(--color-danger);
    
    .toast__icon {
      color: var(--color-danger);
    }
  }
  
  &--warning {
    border-left: 4px solid var(--color-warning);
    
    .toast__icon {
      color: var(--color-warning);
    }
  }
  
  &--info {
    border-left: 4px solid var(--color-primary);
    
    .toast__icon {
      color: var(--color-primary);
    }
  }
}

.toast-enter-active,
.toast-leave-active {
  transition: all var(--transition-normal);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

@media (max-width: 768px) {
  .toast-container {
    left: var(--spacing-md);
    right: var(--spacing-md);
    top: var(--spacing-md);
  }
  
  .toast {
    min-width: auto;
    width: 100%;
  }
}
</style>
