<template>
  <button
    class="btn"
    :class="[
      `btn-${variant}`,
      `btn-${size}`,
      { 'is-loading': loading, 'is-block': block }
    ]"
    :disabled="disabled || loading"
    :type="type"
    @click="handleClick"
  >
    <span v-if="loading" class="btn-loading">
      <span class="spinner"></span>
    </span>
    
    <span v-if="icon && !loading" class="btn-icon">{{ icon }}</span>
    
    <span class="btn-text">
      <slot></slot>
    </span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  type?: 'button' | 'submit' | 'reset';
  disabled?: boolean;
  loading?: boolean;
  block?: boolean;
  icon?: string;
}

interface Emits {
  (e: 'click', event: MouseEvent): void;
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'medium',
  type: 'button',
  disabled: false,
  loading: false,
  block: false
});

const emit = defineEmits<Emits>();

function handleClick(event: MouseEvent) {
  emit('click', event);
}
</script>

<style scoped lang="scss">
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  font-family: var(--font-body);
  font-weight: var(--font-medium);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &.is-loading {
    pointer-events: none;
  }
  
  &.is-block {
    width: 100%;
  }
  
  // Sizes
  &.btn-small {
    padding: var(--spacing-xs) var(--spacing-md);
    font-size: var(--text-sm);
  }
  
  &.btn-medium {
    padding: var(--spacing-sm) var(--spacing-lg);
    font-size: var(--text-base);
  }
  
  &.btn-large {
    padding: var(--spacing-md) var(--spacing-xl);
    font-size: var(--text-lg);
  }
  
  // Variants
  &.btn-primary {
    background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
    color: white;
    box-shadow: var(--shadow-md);
    
    &:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
    }
    
    &:active:not(:disabled) {
      transform: translateY(0);
    }
  }
  
  &.btn-secondary {
    background-color: var(--color-bg-secondary);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
    
    &:hover:not(:disabled) {
      background-color: var(--color-bg-hover);
    }
  }
  
  &.btn-danger {
    background-color: var(--color-error);
    color: white;
    box-shadow: var(--shadow-md);
    
    &:hover:not(:disabled) {
      background-color: #dc2626;
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
    }
  }
  
  &.btn-ghost {
    background-color: transparent;
    color: var(--color-primary);
    
    &:hover:not(:disabled) {
      background-color: var(--color-primary-alpha);
    }
  }
  
  .btn-loading {
    display: inline-flex;
    
    .spinner {
      width: 16px;
      height: 16px;
      border: 2px solid currentColor;
      border-top-color: transparent;
      border-radius: var(--radius-full);
      animation: spin 1s linear infinite;
    }
  }
  
  .btn-icon {
    font-size: 1.2em;
  }
  
  .btn-text {
    display: inline-block;
  }
}
</style>
