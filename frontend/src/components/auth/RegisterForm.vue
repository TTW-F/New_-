<template>
  <form class="register-form" @submit.prevent="handleSubmit">
    <div class="register-form__header">
      <h2 class="register-form__title">注册</h2>
      <p class="register-form__subtitle">创建您的医疗问答账号</p>
    </div>
    
    <!-- 全局错误提示 -->
    <div v-if="globalError" class="global-error">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M10 6V11M10 14H10.01M18 10C18 14.4183 14.4183 18 10 18C5.58172 18 2 14.4183 2 10C2 5.58172 5.58172 2 10 2C14.4183 2 18 5.58172 18 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <span>{{ globalError }}</span>
    </div>
    
    <div class="register-form__body">
      <div class="form-group">
        <label for="reg-username" class="form-label">用户名</label>
        <input
          id="reg-username"
          v-model="formData.username"
          type="text"
          class="form-input"
          :class="{ 'form-input--error': errors.username }"
          placeholder="3-20个字符,字母、数字、下划线"
          autocomplete="username"
          @blur="validateUsername"
          @input="clearGlobalError"
        />
        <span v-if="errors.username" class="form-error">{{ errors.username }}</span>
      </div>
      
      <div class="form-group">
        <label for="reg-email" class="form-label">邮箱</label>
        <input
          id="reg-email"
          v-model="formData.email"
          type="email"
          class="form-input"
          :class="{ 'form-input--error': errors.email }"
          placeholder="请输入邮箱地址"
          autocomplete="email"
          @blur="validateEmail"
          @input="clearGlobalError"
        />
        <span v-if="errors.email" class="form-error">{{ errors.email }}</span>
      </div>
      
      <div class="form-group">
        <label for="reg-password" class="form-label">密码</label>
        <div class="password-input">
          <input
            id="reg-password"
            v-model="formData.password"
            :type="showPassword ? 'text' : 'password'"
            class="form-input"
            :class="{ 'form-input--error': errors.password }"
            placeholder="至少8个字符,包含字母和数字"
            autocomplete="new-password"
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
      
      <div class="form-group">
        <label for="reg-confirm-password" class="form-label">确认密码</label>
        <div class="password-input">
          <input
            id="reg-confirm-password"
            v-model="formData.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'"
            class="form-input"
            :class="{ 'form-input--error': errors.confirmPassword }"
            placeholder="请再次输入密码"
            autocomplete="new-password"
            @blur="validateConfirmPassword"
            @input="clearGlobalError"
          />
          <button
            type="button"
            class="password-toggle"
            @click="showConfirmPassword = !showConfirmPassword"
            aria-label="切换密码可见性"
          >
            <svg v-if="showConfirmPassword" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M2 10C2 10 5 4 10 4C15 4 18 10 18 10C18 10 15 16 10 16C5 16 2 10 2 10Z" stroke="currentColor" stroke-width="1.5"/>
              <circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 3L17 17M10 7C11.6569 7 13 8.34315 13 10C13 10.3506 12.9448 10.6872 12.8433 11M7 10C7 8.34315 8.34315 7 10 7M7 10C7 11.6569 8.34315 13 10 13M7 10L10 13M10 13C10.3506 13 10.6872 12.9448 11 12.8433" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <span v-if="errors.confirmPassword" class="form-error">{{ errors.confirmPassword }}</span>
      </div>
      
      <Button
        type="submit"
        variant="primary"
        :loading="loading"
        :disabled="loading"
        class="register-form__submit"
        @click="handleSubmit"
      >
        注册
      </Button>
      
      <div class="register-form__footer">
        <span class="footer-text">已有账号?</span>
        <button
          type="button"
          class="footer-link"
          @click="$emit('switch-to-login')"
        >
          立即登录
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
  (e: 'switch-to-login'): void;
}

defineEmits<Emits>();

const { register } = useAuth();
const { success, error: showError } = useToast();

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const errors = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const loading = ref(false);
const showPassword = ref(false);
const showConfirmPassword = ref(false);
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

const validateEmail = () => {
  errors.email = validate(formData.email, [
    rules.required('请输入邮箱'),
    rules.email()
  ]) || '';
};

const validatePassword = () => {
  errors.password = validate(formData.password, [
    rules.required('请输入密码'),
    rules.password()
  ]) || '';
};

const validateConfirmPassword = () => {
  if (!formData.confirmPassword) {
    errors.confirmPassword = '请确认密码';
  } else if (formData.password !== formData.confirmPassword) {
    errors.confirmPassword = '两次输入的密码不一致';
  } else {
    errors.confirmPassword = '';
  }
};

const validateForm = (): boolean => {
  validateUsername();
  validateEmail();
  validatePassword();
  validateConfirmPassword();
  
  return !errors.username && !errors.email && !errors.password && !errors.confirmPassword;
};

const handleSubmit = async () => {
  if (!validateForm()) {
    globalError.value =
      errors.username ||
      errors.email ||
      errors.password ||
      errors.confirmPassword ||
      '请检查表单填写项后再试';
    showError(globalError.value, 4000);
    return;
  }

  loading.value = true;
  globalError.value = '';

  try {
    await register({
      username: formData.username,
      email: formData.email,
      password: formData.password
    });
    
    success('注册成功');
  } catch (err) {
    const appError = handleError(err, 'RegisterForm.handleSubmit');
    globalError.value = appError.message;
    showError(appError.message, 5000); // 显示5秒
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped lang="scss">
.register-form {
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
</style>
