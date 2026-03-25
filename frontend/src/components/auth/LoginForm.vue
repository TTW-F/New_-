<template>
  <form class="login-form" @submit.prevent="handleSubmit">
    <div class="login-form__header">
      <h2 class="login-form__title">登录</h2>
      <p class="login-form__subtitle">欢迎回到医疗问答系统</p>
    </div>
    
    <!-- 全局错误提示 -->
    <div v-if="globalError" class="global-error">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M10 6V11M10 14H10.01M18 10C18 14.4183 14.4183 18 10 18C5.58172 18 2 14.4183 2 10C2 5.58172 5.58172 2 10 2C14.4183 2 18 5.58172 18 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <span>{{ globalError }}</span>
    </div>
    
    <div class="login-form__body">
      <div class="form-group">
        <label for="username" class="form-label">用户名</label>
        <input
          id="username"
          v-model="formData.username"
          type="text"
          class="form-input"
          :class="{ 'form-input--error': errors.username }"
          placeholder="请输入用户名"
          autocomplete="username"
          @blur="validateUsername"
          @input="clearGlobalError"
        />
        <span v-if="errors.username" class="form-error">{{ errors.username }}</span>
      </div>
      
      <div class="form-group">
        <label for="password" class="form-label">密码</label>
        <div class="password-input">
          <input
            id="password"
            v-model="formData.password"
            :type="showPassword ? 'text' : 'password'"
            class="form-input"
            :class="{ 'form-input--error': errors.password }"
            placeholder="请输入密码"
            autocomplete="current-password"
            @blur="validatePassword"
            @input="clearGlobalError"
          />
          <button
            type="button"
            class="password-toggle"
            @click="showPassword = !showPassword"
            aria-label="切换密码可见性"
          >
            <svg v-if="showPassword" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M2 10C2 10 5 4 10 4C15 4 18 10 18 10C18 10 15 16 10 16C5 16 2 10 2 10Z" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 3L17 17M10 7C11.6569 7 13 8.34315 13 10C13 10.3506 12.9448 10.6872 12.8433 11M7 10C7 8.34315 8.34315 7 10 7M7 10C7 11.6569 8.34315 13 10 13M7 10L10 13M10 13C10.3506 13 10.6872 12.9448 11 12.8433" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <span v-if="errors.password" class="form-error">{{ errors.password }}</span>
      </div>
      
      <div class="form-group form-group--checkbox">
        <label class="checkbox-label">
          <input
            v-model="formData.rememberMe"
            type="checkbox"
            class="checkbox-input"
          />
          <span class="checkbox-text">记住我</span>
        </label>
      </div>
      
      <Button
        type="submit"
        variant="primary"
        :loading="loading"
        :disabled="loading"
        class="login-form__submit"
        @click="handleSubmit"
      >
        登录
      </Button>
      
      <div class="login-form__footer">
        <span class="footer-text">还没有账号?</span>
        <button
          type="button"
          class="footer-link"
          @click="$emit('switch-to-register')"
        >
          立即注册
        </button>
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useAuth } from '@/composables/useAuth';
import { useToast } from '@/composables/useToast';
import { rules, validate } from '@/utils/validator';
import { handleError } from '@/utils/error-handler';
import Button from '@/components/common/Button.vue';

interface Emits {
  (e: 'switch-to-register'): void;
}

defineEmits<Emits>();

const { login } = useAuth();
const { success, error: showError } = useToast();

const formData = reactive({
  username: '',
  password: '',
  rememberMe: false
});

const errors = reactive({
  username: '',
  password: ''
});

const loading = ref(false);
const showPassword = ref(false);
const globalError = ref('');

const clearGlobalError = () => {
  globalError.value = '';
};

const validateUsername = () => {
  errors.username = validate(formData.username, [
    rules.required('请输入用户名'),
    rules.username()
  ]) || '';
};

const validatePassword = () => {
  errors.password = validate(formData.password, [
    rules.required('请输入密码')
  ]) || '';
};

const validateForm = (): boolean => {
  validateUsername();
  validatePassword();
  return !errors.username && !errors.password;
};

const handleSubmit = async () => {
  if (!validateForm()) {
    globalError.value = errors.username || errors.password || '请检查用户名和密码后再试';
    showError(globalError.value, 4000);
    return;
  }

  loading.value = true;
  globalError.value = '';

  try {
    await login({
      username: formData.username,
      password: formData.password
    });
    
    success('登录成功');
  } catch (err) {
    const appError = handleError(err, 'LoginForm.handleSubmit');
    globalError.value = appError.message;
    showError(appError.message, 5000); // 显示5秒
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped lang="scss">
.login-form {
  width: 100%;
  max-width: 400px;
  
  &__header {
    text-align: center;
    margin-bottom: var(--spacing-xl);
  }
  
  &__title {
    font-size: var(--text-2xl);
    font-weight: var(--font-bold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-sm) 0;
  }
  
  &__subtitle {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    margin: 0;
  }
  
  &__body {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }
  
  &__submit {
    width: 100%;
    margin-top: var(--spacing-md);
  }
  
  &__footer {
    text-align: center;
    padding-top: var(--spacing-lg);
    border-top: 1px solid var(--color-border);
    
    .footer-text {
      font-size: var(--text-sm);
      color: var(--color-text-secondary);
      margin-right: var(--spacing-xs);
    }
    
    .footer-link {
      font-size: var(--text-sm);
      color: var(--color-primary);
      background: none;
      border: none;
      padding: 0;
      cursor: pointer;
      font-weight: var(--font-medium);
      transition: color var(--transition-fast);
      
      &:hover {
        color: var(--color-secondary);
        text-decoration: underline;
      }
    }
  }
}

.global-error {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-md);
  color: var(--color-danger);
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
  animation: shake 0.5s ease-in-out;
  
  svg {
    flex-shrink: 0;
  }
  
  span {
    flex: 1;
  }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  
  &--checkbox {
    flex-direction: row;
    align-items: center;
  }
}

.form-label {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

.form-input {
  width: 100%;
  padding: var(--spacing-md);
  font-size: var(--text-base);
  color: var(--color-text-primary);
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  
  &:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  &--error {
    border-color: var(--color-danger);
    
    &:focus {
      box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }
  }
  
  &::placeholder {
    color: var(--color-text-secondary);
  }
}

.password-input {
  position: relative;
  
  .form-input {
    padding-right: 48px;
  }
  
  .password-toggle {
    position: absolute;
    right: var(--spacing-md);
    top: 50%;
    transform: translateY(-50%);
    width: 32px;
    height: 32px;
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
      background-color: var(--color-bg-tertiary);
      color: var(--color-text-primary);
    }
  }
}

.form-error {
  font-size: var(--text-xs);
  color: var(--color-danger);
  margin-top: calc(var(--spacing-sm) * -0.5);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  user-select: none;
}

.checkbox-input {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-primary);
}

.checkbox-text {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}
</style>
