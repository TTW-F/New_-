<template>
  <div class="not-found">
    <div class="not-found__content">
      <div class="not-found__icon">
        <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
          <circle cx="60" cy="60" r="50" stroke="currentColor" stroke-width="2" opacity="0.2"/>
          <path d="M40 50L50 60L40 70M80 50L70 60L80 70" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
          <path d="M45 85H75" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
        </svg>
      </div>
      
      <h1 class="not-found__title">404</h1>
      <p class="not-found__message">页面未找到</p>
      <p class="not-found__description">
        抱歉,您访问的页面不存在或已被移除
      </p>
      
      <Button
        variant="primary"
        @click="goHome"
      >
        返回首页
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import Button from '@/components/common/Button.vue';

const router = useRouter();

const goHome = () => {
  router.push('/');
};
</script>

<style scoped lang="scss">
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, 
    rgba(59, 130, 246, 0.05) 0%,
    rgba(139, 92, 246, 0.05) 100%
  );
  
  &__content {
    text-align: center;
    max-width: 500px;
  }
  
  &__icon {
    color: var(--color-primary);
    margin-bottom: var(--spacing-xl);
    animation: float 3s ease-in-out infinite;
  }
  
  &__title {
    font-size: 72px;
    font-weight: var(--font-bold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-md) 0;
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  &__message {
    font-size: var(--text-xl);
    font-weight: var(--font-semibold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-md) 0;
  }
  
  &__description {
    font-size: var(--text-base);
    color: var(--color-text-secondary);
    margin: 0 0 var(--spacing-xl) 0;
    line-height: var(--leading-relaxed);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}
</style>
