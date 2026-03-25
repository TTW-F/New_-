<template>
  <div class="profile-view">
    <Navbar />
    <div class="profile-header">
      <h1>个人中心</h1>
    </div>

    <div class="profile-content">
      <div class="profile-card">
        <div class="profile-avatar">
          <div class="avatar-circle">
            {{ userInitial }}
          </div>
        </div>

        <div class="profile-info">
          <h2>{{ authStore.user?.username }}</h2>
          <p class="user-email">{{ authStore.user?.email }}</p>
          <span class="user-badge">{{ userTypeLabel }}</span>
        </div>
      </div>

      <div class="info-section">
        <h3>账户信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <label>用户名</label>
            <div class="info-value">{{ authStore.user?.username }}</div>
          </div>
          <div class="info-item">
            <label>邮箱</label>
            <div class="info-value">{{ authStore.user?.email }}</div>
          </div>
          <div class="info-item">
            <label>用户类型</label>
            <div class="info-value">{{ userTypeLabel }}</div>
          </div>
          <div class="info-item">
            <label>注册时间</label>
            <div class="info-value">{{ formatDate(authStore.user?.created_at) }}</div>
          </div>
        </div>
      </div>

      <div class="password-section">
        <h3>修改密码</h3>
        <form @submit.prevent="handleChangePassword" class="password-form">
          <div class="form-group">
            <label>当前密码</label>
            <input 
              v-model="passwordForm.oldPassword" 
              type="password" 
              placeholder="请输入当前密码"
              required
            />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input 
              v-model="passwordForm.newPassword" 
              type="password" 
              placeholder="请输入新密码（至少6位）"
              required
              minlength="6"
            />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input 
              v-model="passwordForm.confirmPassword" 
              type="password" 
              placeholder="请再次输入新密码"
              required
            />
          </div>
          <button type="submit" class="btn-submit" :disabled="isChangingPassword">
            {{ isChangingPassword ? '修改中...' : '修改密码' }}
          </button>
        </form>
      </div>

      <div class="danger-section">
        <h3>危险操作</h3>
        <button class="btn-logout" @click="handleLogout">
          退出登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import Navbar from '@/components/common/Navbar.vue';
import { changePassword } from '@/api/user';

const router = useRouter();
const authStore = useAuthStore();
const { showToast } = useToast();
const { showConfirm } = useConfirm();

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const isChangingPassword = ref(false);

const userInitial = computed(() => {
  return authStore.user?.username?.charAt(0).toUpperCase() || 'U';
});

const userTypeLabel = computed(() => {
  const typeMap: Record<string, string> = {
    'patient': '患者',
    'doctor': '医生',
    'admin': '管理员'
  };
  return typeMap[authStore.user?.user_type || 'patient'] || '患者';
});

const formatDate = (dateString?: string) => {
  if (!dateString) return '未知';
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const handleChangePassword = async () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    showToast('两次输入的密码不一致', 'error');
    return;
  }

  if (passwordForm.value.newPassword.length < 6) {
    showToast('新密码至少需要6位', 'error');
    return;
  }

  isChangingPassword.value = true;
  try {
    await changePassword(
      passwordForm.value.oldPassword,
      passwordForm.value.newPassword
    );
    
    showToast('密码修改成功，请重新登录', 'success');
    
    // 清空表单
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    };
    
    // 延迟后退出登录
    setTimeout(() => {
      authStore.logout();
      router.push({ name: 'Login' });
    }, 1500);
  } catch (error: any) {
    const errorMessage = error.response?.data?.detail || '密码修改失败';
    showToast(errorMessage, 'error');
  } finally {
    isChangingPassword.value = false;
  }
};

const handleLogout = async () => {
  const confirmed = await showConfirm(
    '确认退出',
    '确定要退出登录吗？',
    '',
    'warning'
  );

  if (confirmed) {
    await authStore.logout();
    router.push({ name: 'Login' });
    showToast('已退出登录', 'success');
  }
};
</script>

<style scoped lang="scss">
.profile-view {
  width: 100%;
  min-height: 100vh;
  background: #f5f5f5;
}

.profile-header {
  background: white;
  padding: 24px 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;

  h1 {
    font-size: 24px;
    color: #333;
  }

  .btn-back {
    padding: 8px 20px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background: #5568d3;
    }
  }
}

.profile-content {
  max-width: 700px;
  margin: 0 auto;
  padding: 24px 20px;
}

.profile-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .profile-avatar {
    margin-bottom: 24px;

    .avatar-circle {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-size: 48px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto;
    }
  }

  .profile-info {
    h2 {
      font-size: 28px;
      color: #333;
      margin-bottom: 8px;
    }

    .user-email {
      font-size: 16px;
      color: #666;
      margin-bottom: 16px;
    }

    .user-badge {
      display: inline-block;
      padding: 6px 16px;
      background: #667eea;
      color: white;
      border-radius: 20px;
      font-size: 14px;
    }
  }
}

.info-section,
.password-section,
.danger-section {
  background: white;
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  h3 {
    font-size: 20px;
    color: #333;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 2px solid #f0f0f0;
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.info-item {
  label {
    display: block;
    font-size: 14px;
    color: #999;
    margin-bottom: 8px;
  }

  .info-value {
    font-size: 16px;
    color: #333;
    font-weight: 500;
  }
}

.password-form {
  max-width: 500px;

  .form-group {
    margin-bottom: 20px;

    label {
      display: block;
      font-size: 14px;
      color: #333;
      margin-bottom: 8px;
      font-weight: 500;
    }

    input {
      width: 100%;
      padding: 12px 16px;
      border: 1px solid #ddd;
      border-radius: 8px;
      font-size: 14px;
      transition: all 0.3s;

      &:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }
    }
  }

  .btn-submit {
    width: 100%;
    padding: 12px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover:not(:disabled) {
      background: #5568d3;
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
}

.danger-section {
  .btn-logout {
    padding: 12px 32px;
    background: #ff4d4f;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background: #ff7875;
    }
  }
}
</style>
