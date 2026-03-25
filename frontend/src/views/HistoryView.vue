<template>
  <div class="history-view">
    <Navbar />
    <div class="history-header">
      <h1>对话历史</h1>
    </div>

    <div class="history-content">
      <div class="history-filters">
        <input 
          v-model="searchKeyword" 
          type="text" 
          placeholder="搜索对话内容..."
          class="search-input"
          @input="handleSearch"
        />
      </div>

      <div v-if="loading" class="loading-state">
        <Loading />
        <p>加载中...</p>
      </div>

      <div v-else-if="sessions.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>暂无对话历史</p>
        <button class="btn-primary" @click="startNewChat">开始新对话</button>
      </div>

      <div v-else class="session-list">
        <div 
          v-for="session in sessions" 
          :key="session.session_id"
          class="session-card"
        >
          <div class="session-header">
            <div class="session-info">
              <h3>{{ session.title || '医疗咨询' }}</h3>
              <span class="session-time">{{ formatTime(session.updated_at) }}</span>
            </div>
            <div class="session-actions">
              <button class="btn-continue" @click="continueSession(session.session_id)">
                继续对话
              </button>
              <button class="btn-delete" @click="confirmDelete(session.session_id)">
                删除
              </button>
            </div>
          </div>

          <div class="session-stats">
            <span>💬 {{ session.message_count || 0 }} 条消息</span>
            <span>⏱️ 平均响应 {{ session.avg_response_time || 0 }}ms</span>
          </div>

          <div class="session-preview">
            <div class="preview-item">
              <strong>最后提问：</strong>
              {{ session.last_question || '无' }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="totalPages > 1" class="pagination">
        <button 
          :disabled="currentPage === 1" 
          @click="changePage(currentPage - 1)"
          class="btn-page"
        >
          上一页
        </button>
        <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
        <button 
          :disabled="currentPage === totalPages" 
          @click="changePage(currentPage + 1)"
          class="btn-page"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getSessionList, deleteSession } from '@/api/history';
import { formatDistanceToNow } from '@/utils/format';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import Loading from '@/components/common/Loading.vue';
import Navbar from '@/components/common/Navbar.vue';

const router = useRouter();
const { showToast } = useToast();
const { showConfirm } = useConfirm();

const sessions = ref<any[]>([]);
const loading = ref(false);
const currentPage = ref(1);
const totalPages = ref(1);
const searchKeyword = ref('');

const startNewChat = () => {
  router.push({ name: 'Chat' });
};

const continueSession = (sessionId: string) => {
  router.push({ name: 'Chat', query: { session: sessionId } });
};

const formatTime = (time: string) => {
  return formatDistanceToNow(new Date(time));
};

const loadSessions = async () => {
  loading.value = true;
  try {
    const response = await getSessionList(currentPage.value, 10);
    sessions.value = response.sessions || [];
    totalPages.value = Math.ceil((response.total || 0) / 10);
  } catch (error) {
    showToast('加载历史记录失败', 'error');
  } finally {
    loading.value = false;
  }
};

const changePage = (page: number) => {
  currentPage.value = page;
  loadSessions();
};

const handleSearch = () => {
  currentPage.value = 1;
  loadSessions();
};

const confirmDelete = async (sessionId: string) => {
  const confirmed = await showConfirm(
    '确认删除',
    '确定要删除这个对话吗？',
    '此操作不可恢复',
    'warning'
  );

  if (confirmed) {
    await handleDelete(sessionId);
  }
};

const handleDelete = async (sessionId: string) => {
  try {
    await deleteSession(sessionId);
    showToast('删除成功', 'success');
    loadSessions();
  } catch (error) {
    showToast('删除失败', 'error');
  }
};

onMounted(() => {
  loadSessions();
});
</script>

<style scoped lang="scss">
.history-view {
  width: 100%;
  min-height: 100vh;
  background: var(--color-bg-secondary);
}

.history-header {
  background: var(--color-bg-primary);
  padding: 24px 32px;
  box-shadow: var(--shadow-md);
  border-bottom: 1px solid var(--color-border);

  h1 {
    font-size: var(--text-2xl);
    color: var(--color-text-primary);
  }
}

.history-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px 20px;
}

.history-filters {
  margin-bottom: 24px;

  .search-input {
    width: 100%;
    max-width: 400px;
    padding: 12px 16px;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);

    &:focus {
      outline: none;
      border-color: var(--color-primary);
    }
  }
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);

  .empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
    color: var(--color-text-tertiary);
  }

  p {
    font-size: var(--text-base);
    color: var(--color-text-secondary);
    margin-bottom: 24px;
  }

  .btn-primary {
    padding: 12px 32px;
    background: var(--color-primary);
    color: white;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    font-size: var(--text-sm);
    font-weight: var(--font-medium);

    &:hover {
      background: var(--color-primary-dark);
    }
  }
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.session-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
  transition: all var(--transition-base);

  &:hover {
    box-shadow: var(--shadow-lg);
    border-color: var(--color-primary);
  }

  .session-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;

    .session-info {
      h3 {
        font-size: var(--text-lg);
        color: var(--color-text-primary);
        margin-bottom: 8px;
      }

      .session-time {
        font-size: var(--text-sm);
        color: var(--color-text-tertiary);
      }
    }

    .session-actions {
      display: flex;
      gap: 8px;

      button {
        padding: 8px 16px;
        border: none;
        border-radius: var(--radius-md);
        cursor: pointer;
        font-size: var(--text-sm);
        transition: all var(--transition-fast);
        font-weight: var(--font-medium);

        &.btn-continue {
          background: var(--color-primary);
          color: white;

          &:hover {
            background: var(--color-primary-dark);
          }
        }

        &.btn-delete {
          background: var(--color-bg-tertiary);
          color: var(--color-text-secondary);

          &:hover {
            background: var(--color-error);
            color: white;
          }
        }
      }
    }
  }

  .session-stats {
    display: flex;
    gap: 24px;
    margin-bottom: 16px;
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
  }

  .session-preview {
    .preview-item {
      font-size: var(--text-sm);
      color: var(--color-text-secondary);
      line-height: var(--leading-relaxed);

      strong {
        color: var(--color-text-primary);
      }
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;

  .btn-page {
    padding: 8px 16px;
    background: var(--color-bg-primary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-fast);
    font-size: var(--text-sm);

    &:hover:not(:disabled) {
      border-color: var(--color-primary);
      color: var(--color-primary);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  .page-info {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
  }
}
</style>
