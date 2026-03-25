<template>
  <div class="loading" :class="[`size-${size}`, `type-${type}`]">
    <div v-if="type === 'spinner'" class="spinner"></div>
    <div v-else-if="type === 'pulse'" class="pulse"></div>
    <div v-else-if="type === 'dots'" class="dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
    
    <p v-if="text" class="loading-text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'small' | 'medium' | 'large';
  type?: 'spinner' | 'pulse' | 'dots';
  text?: string;
}

withDefaults(defineProps<Props>(), {
  size: 'medium',
  type: 'spinner'
});
</script>

<style scoped lang="scss">
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  
  &.size-small {
    .spinner, .pulse {
      width: 24px;
      height: 24px;
    }
    
    .dots span {
      width: 6px;
      height: 6px;
    }
  }
  
  &.size-medium {
    .spinner, .pulse {
      width: 40px;
      height: 40px;
    }
    
    .dots span {
      width: 10px;
      height: 10px;
    }
  }
  
  &.size-large {
    .spinner, .pulse {
      width: 60px;
      height: 60px;
    }
    
    .dots span {
      width: 14px;
      height: 14px;
    }
  }
  
  .spinner {
    border: 3px solid var(--color-border);
    border-top-color: var(--color-primary);
    border-radius: var(--radius-full);
    animation: spin 1s linear infinite;
  }
  
  .pulse {
    background-color: var(--color-primary);
    border-radius: var(--radius-full);
    animation: pulse 2s ease-in-out infinite;
  }
  
  .dots {
    display: flex;
    gap: var(--spacing-xs);
    
    span {
      background-color: var(--color-primary);
      border-radius: var(--radius-full);
      animation: pulse 1.4s ease-in-out infinite;
      
      &:nth-child(1) {
        animation-delay: 0s;
      }
      
      &:nth-child(2) {
        animation-delay: 0.2s;
      }
      
      &:nth-child(3) {
        animation-delay: 0.4s;
      }
    }
  }
  
  .loading-text {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    text-align: center;
  }
}
</style>
