<template>
  <div class="home-view">
    <Navbar />
    <div class="home-header">
      <div class="header-content">
        <h1 class="title">医疗诊断智能问答系统</h1>
        <p class="subtitle">基于知识图谱的智能医疗助手</p>
        <div class="header-actions">
          <button class="btn-primary" @click="startChat">开始咨询</button>
          <button class="btn-secondary" @click="viewHistory">历史记录</button>
        </div>
      </div>
    </div>

    <div class="home-content">
      <div class="feature-section">
        <h2>系统特点</h2>
        <div class="feature-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3>知识图谱</h3>
            <p>基于Neo4j构建的医疗知识图谱，包含疾病、症状、药品等实体及其关系</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3>智能问答</h3>
            <p>采用GraphRAG技术，结合大语言模型提供准确的医疗咨询服务</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3>多轮对话</h3>
            <p>支持上下文理解，可进行连续的多轮对话，提供更精准的建议</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3>实体识别</h3>
            <p>自动识别问题中的医疗实体，提供结构化的诊断信息</p>
          </div>
        </div>
      </div>

      <div class="recent-section" v-if="recentSessions.length > 0">
        <h2>最近对话</h2>
        <div class="recent-list">
          <div 
            v-for="session in recentSessions" 
            :key="session.session_id"
            class="recent-item"
            @click="continueSession(session.session_id)"
          >
            <div class="recent-info">
              <div class="recent-title">{{ session.title || '医疗咨询' }}</div>
              <div class="recent-time">{{ formatTime(session.updated_at) }}</div>
            </div>
            <div class="recent-preview">{{ session.last_question }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { getSessionList } from '@/api/history';
import { formatDistanceToNow } from '@/utils/format';
import Navbar from '@/components/common/Navbar.vue';

const router = useRouter();
const authStore = useAuthStore();

const recentSessions = ref<any[]>([]);

const startChat = () => {
  router.push({ name: 'Chat' });
};

const viewHistory = () => {
  router.push({ name: 'History' });
};

const continueSession = (sessionId: string) => {
  router.push({ name: 'Chat', query: { session: sessionId } });
};

const formatTime = (time: string) => {
  return formatDistanceToNow(new Date(time));
};

const loadRecentSessions = async () => {
  try {
    const response = await getSessionList(1, 5);
    recentSessions.value = response.sessions || [];
  } catch (error) {
    console.error('加载最近对话失败:', error);
  }
};

onMounted(() => {
  if (authStore.isAuthenticated) {
    loadRecentSessions();
  }
});
</script>

<style scoped lang="scss">
.home-view {
  width: 100%;
  min-height: 100vh;
  background: var(--color-bg-secondary);
}

.home-header {
  padding: 80px 20px 60px;
  text-align: center;
  background: linear-gradient(135deg, 
    rgba(37, 99, 235, 0.1) 0%,
    rgba(59, 130, 246, 0.1) 100%
  );
  color: var(--color-text-primary);

  .title {
    font-size: var(--text-4xl);
    font-weight: var(--font-bold);
    margin-bottom: 16px;
  }

  .subtitle {
    font-size: var(--text-xl);
    color: var(--color-text-secondary);
    margin-bottom: 40px;
  }

  .header-actions {
    display: flex;
    gap: 16px;
    justify-content: center;

    button {
      padding: 14px 32px;
      font-size: var(--text-base);
      border-radius: var(--radius-md);
      border: none;
      cursor: pointer;
      transition: all var(--transition-fast);
      font-weight: var(--font-medium);

      &.btn-primary {
        background: var(--color-primary);
        color: white;

        &:hover {
          background: var(--color-primary-dark);
          transform: translateY(-2px);
          box-shadow: var(--shadow-lg);
        }
      }

      &.btn-secondary {
        background: white;
        color: var(--color-primary);
        border: 2px solid var(--color-primary);

        &:hover {
          background: var(--color-primary-alpha);
        }
      }
    }
  }
}

.home-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px 20px;
}

.feature-section,
.recent-section {
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  padding: 40px;
  margin-bottom: 32px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);

  h2 {
    font-size: var(--text-2xl);
    margin-bottom: 24px;
    color: var(--color-text-primary);
  }
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.feature-card {
  text-align: center;
  padding: 24px;
  border-radius: var(--radius-lg);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  transition: all var(--transition-base);

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--color-primary);
  }

  .feature-icon {
    width: 48px;
    height: 48px;
    margin: 0 auto 16px;
    
    svg {
      width: 100%;
      height: 100%;
      color: var(--color-primary);
    }
  }

  h3 {
    font-size: var(--text-lg);
    margin-bottom: 12px;
    color: var(--color-text-primary);
  }

  p {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    line-height: var(--leading-relaxed);
  }
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  padding: 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover {
    border-color: var(--color-primary);
    background: var(--color-primary-alpha);
  }

  .recent-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;

    .recent-title {
      font-weight: var(--font-semibold);
      color: var(--color-text-primary);
    }

    .recent-time {
      font-size: var(--text-sm);
      color: var(--color-text-tertiary);
    }
  }

  .recent-preview {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}
</style>
