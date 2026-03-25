<template>
  <div class="admin-view">
    <Navbar />
    
    <div class="admin-container">
      <div class="admin-header">
        <h1>系统管理</h1>
        <p>管理系统状态和用户信息</p>
      </div>

      <div class="admin-content">
        <!-- 系统状态 -->
        <section class="section">
          <h2>系统状态</h2>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-label">总用户数</div>
              <div class="stat-value">{{ stats.totalUsers }}</div>
              <div class="stat-meta">今日新增: {{ stats.todayUsers }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">对话总数</div>
              <div class="stat-value">{{ stats.totalConversations }}</div>
              <div class="stat-meta">今日对话: {{ stats.todayConversations }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">知识库实体</div>
              <div class="stat-value">{{ stats.totalEntities }}</div>
              <div class="stat-meta">疾病/症状/药品</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">系统状态</div>
              <div class="stat-value status">{{ stats.systemStatus === 'running' ? '运行中' : '异常' }}</div>
              <div class="stat-meta">正常运行</div>
            </div>
          </div>
        </section>

        <!-- 用户管理 -->
        <section class="section">
          <div class="section-header">
            <h2>用户管理</h2>
            <div class="search-box">
              <input 
                v-model="userSearch" 
                type="text" 
                placeholder="搜索用户名或邮箱..." 
                @keyup.enter="loadUsers"
              />
              <button @click="loadUsers" :disabled="loading">
                {{ loading ? '搜索中...' : '搜索' }}
              </button>
            </div>
          </div>

          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>用户名</th>
                  <th>邮箱</th>
                  <th>类型</th>
                  <th>状态</th>
                  <th>注册时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="loading">
                  <td colspan="7" class="loading-cell">加载中...</td>
                </tr>
                <tr v-else-if="users.length === 0">
                  <td colspan="7" class="empty-cell">暂无用户数据</td>
                </tr>
                <tr v-else v-for="user in users" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.email }}</td>
                  <td>
                    <span :class="['badge', `badge-${user.user_type}`]">
                      {{ getUserTypeLabel(user.user_type) }}
                    </span>
                  </td>
                  <td>
                    <span :class="['status-badge', user.is_active ? 'active' : 'inactive']">
                      {{ user.is_active ? '正常' : '禁用' }}
                    </span>
                  </td>
                  <td>{{ formatDateTime(user.created_at) }}</td>
                  <td>
                    <button class="btn-action" @click="viewUserDetail(user)">详情</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pagination" v-if="userTotal > 0">
            <span>共 {{ userTotal }} 个用户</span>
          </div>
        </section>
      </div>
    </div>

    <!-- 用户详情弹窗 -->
    <Modal v-model="showUserModal" title="用户详情">
      <div v-if="selectedUser" class="user-detail">
        <div class="detail-row">
          <label>用户ID:</label>
          <span>{{ selectedUser.id }}</span>
        </div>
        <div class="detail-row">
          <label>用户名:</label>
          <span>{{ selectedUser.username }}</span>
        </div>
        <div class="detail-row">
          <label>邮箱:</label>
          <span>{{ selectedUser.email }}</span>
        </div>
        <div class="detail-row">
          <label>用户类型:</label>
          <span>{{ getUserTypeLabel(selectedUser.user_type) }}</span>
        </div>
        <div class="detail-row">
          <label>账号状态:</label>
          <span :class="['status-text', selectedUser.is_active ? 'active' : 'inactive']">
            {{ selectedUser.is_active ? '正常' : '禁用' }}
          </span>
        </div>
        <div class="detail-row">
          <label>注册时间:</label>
          <span>{{ formatDateTime(selectedUser.created_at) }}</span>
        </div>
        <div class="detail-row">
          <label>更新时间:</label>
          <span>{{ formatDateTime(selectedUser.updated_at) }}</span>
        </div>
        <div v-if="selectedUser.stats" class="detail-section">
          <h4>使用统计</h4>
          <div class="detail-row">
            <label>对话数量:</label>
            <span>{{ selectedUser.stats.conversation_count }}</span>
          </div>
          <div class="detail-row">
            <label>反馈数量:</label>
            <span>{{ selectedUser.stats.feedback_count }}</span>
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from '@/composables/useToast';
import Navbar from '@/components/common/Navbar.vue';
import Modal from '@/components/common/Modal.vue';
import * as adminApi from '@/api/admin';

const { showToast } = useToast();

// 加载状态
const loading = ref(false);

// 统计数据
const stats = ref({
  totalUsers: 0,
  todayUsers: 0,
  totalConversations: 0,
  todayConversations: 0,
  totalEntities: 0,
  systemStatus: 'loading'
});

// 用户管理
const users = ref<adminApi.UserListItem[]>([]);
const userSearch = ref('');
const showUserModal = ref(false);
const selectedUser = ref<adminApi.UserDetail | null>(null);
const userTotal = ref(0);
const userPage = ref(1);
const userPageSize = ref(20);

// 加载统计数据
const loadStats = async () => {
  try {
    const data = await adminApi.getStats();
    stats.value = {
      totalUsers: data.total_users,
      todayUsers: data.today_users,
      totalConversations: data.total_conversations,
      todayConversations: data.today_conversations,
      totalEntities: data.total_entities,
      systemStatus: data.system_status
    };
  } catch (error: any) {
    console.error('加载统计数据失败:', error);
    showToast(error.response?.data?.message || '加载统计数据失败', 'error');
  }
};

// 加载用户列表
const loadUsers = async () => {
  try {
    loading.value = true;
    const data = await adminApi.getUsers({
      search: userSearch.value || undefined,
      page: userPage.value,
      page_size: userPageSize.value
    });
    users.value = data.users;
    userTotal.value = data.total;
  } catch (error: any) {
    console.error('加载用户列表失败:', error);
    showToast(error.response?.data?.message || '加载用户列表失败', 'error');
  } finally {
    loading.value = false;
  }
};

// 查看用户详情
const viewUserDetail = async (user: adminApi.UserListItem) => {
  try {
    loading.value = true;
    const detail = await adminApi.getUserDetail(user.id);
    selectedUser.value = detail;
    showUserModal.value = true;
  } catch (error: any) {
    console.error('加载用户详情失败:', error);
    showToast(error.response?.data?.message || '加载用户详情失败', 'error');
  } finally {
    loading.value = false;
  }
};

// 工具函数
const getUserTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    'admin': '管理员',
    'doctor': '医生',
    'patient': '患者'
  };
  return typeMap[type] || type;
};

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 页面加载时初始化
onMounted(async () => {
  await loadStats();
  await loadUsers();
});
</script>

<style scoped lang="scss">
.admin-view {
  width: 100%;
  min-height: 100vh;
  background: var(--color-bg-secondary);
}

.admin-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 20px;
}

.admin-header {
  text-align: center;
  margin-bottom: 48px;

  h1 {
    font-size: var(--text-3xl);
    font-weight: var(--font-bold);
    color: var(--color-text-primary);
    margin-bottom: 8px;
  }

  p {
    font-size: var(--text-base);
    color: var(--color-text-secondary);
  }
}

.admin-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.section {
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  padding: 32px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);

  h2 {
    font-size: var(--text-2xl);
    font-weight: var(--font-semibold);
    color: var(--color-text-primary);
    margin-bottom: 24px;
  }
}

// 统计卡片
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.stat-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  transition: all var(--transition-base);

  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    border-color: var(--color-primary);
  }

  .stat-label {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: var(--text-3xl);
    font-weight: var(--font-bold);
    color: var(--color-primary);
    margin-bottom: 8px;

    &.status {
      font-size: var(--text-xl);
      color: #10b981;
    }
  }

  .stat-meta {
    font-size: var(--text-xs);
    color: var(--color-text-tertiary);
  }
}

// 区域头部
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h2 {
    margin: 0;
  }

  .search-box {
    display: flex;
    gap: 12px;

    input {
      padding: 10px 16px;
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      font-size: var(--text-sm);
      width: 280px;
      transition: all var(--transition-fast);

      &:focus {
        outline: none;
        border-color: var(--color-primary);
        box-shadow: 0 0 0 3px var(--color-primary-alpha);
      }
    }

    button {
      padding: 10px 24px;
      background: var(--color-primary);
      color: white;
      border: none;
      border-radius: var(--radius-md);
      font-size: var(--text-sm);
      cursor: pointer;
      transition: all var(--transition-fast);
      font-weight: var(--font-medium);

      &:hover:not(:disabled) {
        background: var(--color-primary-dark);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }
  }
}

// 表格样式
.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;

  thead {
    background: var(--color-bg-secondary);

    th {
      padding: 14px 16px;
      text-align: left;
      font-size: var(--text-sm);
      font-weight: var(--font-semibold);
      color: var(--color-text-primary);
      border-bottom: 2px solid var(--color-border);
    }
  }

  tbody {
    tr {
      border-bottom: 1px solid var(--color-border);
      transition: all var(--transition-fast);

      &:hover {
        background: var(--color-bg-secondary);
      }

      td {
        padding: 14px 16px;
        font-size: var(--text-sm);
        color: var(--color-text-secondary);
      }
    }

    .loading-cell,
    .empty-cell {
      text-align: center;
      padding: 40px;
      color: var(--color-text-tertiary);
    }
  }

  .badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);

    &.badge-admin {
      background: rgba(239, 68, 68, 0.1);
      color: #dc2626;
    }

    &.badge-doctor {
      background: rgba(34, 197, 94, 0.1);
      color: #16a34a;
    }

    &.badge-patient {
      background: rgba(59, 130, 246, 0.1);
      color: var(--color-primary);
    }
  }

  .status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);

    &.active {
      background: rgba(34, 197, 94, 0.1);
      color: #16a34a;
    }

    &.inactive {
      background: rgba(239, 68, 68, 0.1);
      color: #dc2626;
    }
  }

  .btn-action {
    padding: 6px 16px;
    background: var(--color-primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    font-size: var(--text-xs);
    cursor: pointer;
    transition: all var(--transition-fast);
    font-weight: var(--font-medium);

    &:hover {
      background: var(--color-primary-dark);
    }
  }
}

// 分页
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px 0;
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

// 用户详情
.user-detail {
  .detail-row {
    display: flex;
    padding: 14px 0;
    border-bottom: 1px solid var(--color-border);

    label {
      width: 120px;
      font-weight: var(--font-semibold);
      color: var(--color-text-primary);
      font-size: var(--text-sm);
    }

    span {
      flex: 1;
      color: var(--color-text-secondary);
      font-size: var(--text-sm);
    }

    .status-text {
      font-weight: var(--font-semibold);

      &.active {
        color: #16a34a;
      }

      &.inactive {
        color: #dc2626;
      }
    }
  }

  .detail-section {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 2px solid var(--color-border);

    h4 {
      font-size: var(--text-base);
      font-weight: var(--font-semibold);
      color: var(--color-text-primary);
      margin-bottom: 16px;
    }
  }
}

@media (max-width: 768px) {
  .admin-container {
    padding: 20px 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;

    .search-box {
      width: 100%;

      input {
        flex: 1;
      }
    }
  }

  .table-container {
    font-size: var(--text-xs);
  }
}
</style>
