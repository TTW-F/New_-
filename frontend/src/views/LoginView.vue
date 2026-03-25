<template>
  <div class="login-view">
    <div class="login-view__background">
      <div class="background-gradient"></div>
      <div class="background-pattern"></div>
    </div>
    
    <div class="login-view__container">
      <div class="login-view__card">
        <div class="card-logo">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <rect width="48" height="48" rx="12" fill="url(#logo-gradient)"/>
            <path d="M24 14V34M14 24H34" stroke="white" stroke-width="3" stroke-linecap="round"/>
            <defs>
              <linearGradient id="logo-gradient" x1="0" y1="0" x2="48" y2="48">
                <stop offset="0%" stop-color="#3B82F6"/>
                <stop offset="100%" stop-color="#8B5CF6"/>
              </linearGradient>
            </defs>
          </svg>
          <h1 class="logo-text">医疗问答系统</h1>
        </div>
        
        <Transition name="form-switch" mode="out-in">
          <LoginForm
            v-if="currentForm === 'login'"
            key="login"
            @switch-to-register="currentForm = 'register'"
          />
          <RegisterForm
            v-else
            key="register"
            @switch-to-login="currentForm = 'login'"
          />
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import LoginForm from '@/components/auth/LoginForm.vue';
import RegisterForm from '@/components/auth/RegisterForm.vue';

const currentForm = ref<'login' | 'register'>('login');
</script>

<style scoped lang="scss">
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  
  &__background {
    position: absolute;
    inset: 0;
    z-index: 0;
    
    .background-gradient {
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, 
        rgba(59, 130, 246, 0.1) 0%,
        rgba(139, 92, 246, 0.1) 100%
      );
    }
    
    .background-pattern {
      position: absolute;
      inset: 0;
      background-image: 
        radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.05) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 50%);
    }
  }
  
  &__container {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 480px;
    padding: var(--spacing-lg);
  }
  
  &__card {
    background-color: var(--color-bg-primary);
    border-radius: var(--radius-2xl);
    box-shadow: var(--shadow-2xl);
    padding: var(--spacing-2xl);
    border: 1px solid var(--color-border);
    
    .card-logo {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: var(--spacing-md);
      margin-bottom: var(--spacing-2xl);
      
      .logo-text {
        font-size: var(--text-xl);
        font-weight: var(--font-bold);
        color: var(--color-text-primary);
        margin: 0;
      }
    }
  }
}

.form-switch-enter-active,
.form-switch-leave-active {
  transition: all var(--transition-normal);
}

.form-switch-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.form-switch-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

@media (max-width: 768px) {
  .login-view {
    &__container {
      padding: var(--spacing-md);
    }
    
    &__card {
      padding: var(--spacing-xl);
    }
  }
}
</style>
