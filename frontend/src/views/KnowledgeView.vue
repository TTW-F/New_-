<template>
  <div class="knowledge-view">
    <Navbar />
    <div class="knowledge-header">
      <h1>医疗知识库</h1>
      <div class="view-tabs">
        <button 
          :class="['tab-btn', { active: currentView === 'search' }]"
          @click="currentView = 'search'"
        >
          搜索浏览
        </button>
        <button 
          :class="['tab-btn', { active: currentView === 'graph' }]"
          @click="currentView = 'graph'"
        >
          图谱视图
        </button>
      </div>
    </div>

    <div class="knowledge-content">
      <!-- 搜索视图 -->
      <div v-show="currentView === 'search'" class="search-view">
      <div class="search-section">
        <div class="search-box">
          <input 
            v-model="searchKeyword" 
            type="text" 
            placeholder="搜索疾病、症状、药品..."
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch" class="btn-search">搜索</button>
        </div>
        <div class="search-filters">
          <button 
            v-for="type in entityTypes" 
            :key="type.value"
            :class="['filter-btn', { active: selectedType === type.value }]"
            @click="selectType(type.value)"
          >
            {{ type.label }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <Loading />
        <p>加载中...</p>
      </div>

      <div v-else-if="searchResults.length === 0 && hasSearched" class="empty-state">
        <div class="empty-icon">🔍</div>
        <p>未找到相关结果</p>
        <p class="empty-hint">试试搜索"感冒"、"头痛"或"阿司匹林"</p>
      </div>

      <div v-else-if="searchResults.length > 0" class="results-section">
        <h2>搜索结果 ({{ searchResults.length }})</h2>
        <div class="results-grid">
          <div 
            v-for="item in searchResults" 
            :key="item.name"
            class="result-card"
            @click="viewDetail(item)"
          >
            <div class="card-header">
              <span class="entity-type" :class="item.type.toLowerCase()">
                {{ getTypeLabel(item.type) }}
              </span>
              <h3>{{ item.name }}</h3>
            </div>
            <div class="card-body">
              <p>{{ item.description || '暂无描述' }}</p>
            </div>
            <div class="card-footer">
              <span class="view-detail">查看详情 →</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="intro-section">
        <h2>知识库统计</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <svg class="stat-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="stat-value">10,000+</div>
            <div class="stat-label">疾病</div>
          </div>
          <div class="stat-card">
            <svg class="stat-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="stat-value">5,000+</div>
            <div class="stat-label">药品</div>
          </div>
          <div class="stat-card">
            <svg class="stat-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="stat-value">3,000+</div>
            <div class="stat-label">症状</div>
          </div>
          <div class="stat-card">
            <svg class="stat-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="stat-value">2,000+</div>
            <div class="stat-label">检查项</div>
          </div>
        </div>

        <div class="popular-section">
          <h3>热门疾病</h3>
          <div class="popular-grid">
            <div 
              v-for="item in popularDiseases" 
              :key="item.name"
              class="popular-card"
              @click="viewDetail(item)"
            >
              <div class="card-header">
                <span class="entity-type disease">疾病</span>
                <h4>{{ item.name }}</h4>
              </div>
              <p class="card-desc">{{ item.description }}</p>
            </div>
          </div>
        </div>

        <div class="popular-section">
          <h3>常见症状</h3>
          <div class="popular-grid">
            <div 
              v-for="item in popularSymptoms" 
              :key="item.name"
              class="popular-card"
              @click="viewDetail(item)"
            >
              <div class="card-header">
                <span class="entity-type symptom">症状</span>
                <h4>{{ item.name }}</h4>
              </div>
              <p class="card-desc">{{ item.description }}</p>
            </div>
          </div>
        </div>

        <div class="popular-section">
          <h3>常用药品</h3>
          <div class="popular-grid">
            <div 
              v-for="item in popularDrugs" 
              :key="item.name"
              class="popular-card"
              @click="viewDetail(item)"
            >
              <div class="card-header">
                <span class="entity-type drug">药品</span>
                <h4>{{ item.name }}</h4>
              </div>
              <p class="card-desc">{{ item.description }}</p>
            </div>
          </div>
        </div>

        <div class="examples-section">
          <h3>快速搜索</h3>
          <div class="example-tags">
            <span 
              v-for="example in examples" 
              :key="example"
              class="example-tag"
              @click="searchExample(example)"
            >
              {{ example }}
            </span>
          </div>
        </div>
      </div>
      </div>

      <!-- 图谱视图 -->
      <div v-show="currentView === 'graph'" class="graph-view">
        <div class="graph-search">
          <input 
            v-model="graphSearchKeyword" 
            type="text" 
            placeholder="输入实体名称查看关系图谱..."
            @keyup.enter="handleGraphSearch"
          />
          <button @click="handleGraphSearch" class="btn-search">查看图谱</button>
        </div>

        <div v-if="!graphEntityName" class="graph-intro">
          <div class="intro-icon">🕸️</div>
          <h3>知识图谱可视化</h3>
          <p>输入疾病、症状或药品名称,查看它们之间的关联关系</p>
          <div class="example-searches">
            <span 
              v-for="example in graphExamples" 
              :key="example"
              class="example-tag"
              @click="searchGraph(example)"
            >
              {{ example }}
            </span>
          </div>
        </div>

        <KnowledgeGraph
          v-else
          :entity-name="graphEntityName"
          :entity-type="graphEntityType"
          @node-click="handleGraphNodeClick"
        />
      </div>
    </div>

    <!-- 详情弹窗 -->
    <Modal v-model="showDetailModal" :title="selectedItem?.name || '详情'">
      <div v-if="selectedItem" class="detail-content">
        <div class="detail-section">
          <h4>基本信息</h4>
          <p><strong>名称：</strong>{{ selectedItem.name }}</p>
          <p><strong>类型：</strong>{{ getTypeLabel(selectedItem.type) }}</p>
          <p v-if="selectedItem.description">
            <strong>描述：</strong>{{ selectedItem.description }}
          </p>
        </div>
        <div class="detail-actions">
          <button class="btn-ask" @click="askAbout(selectedItem.name)">
            向AI咨询
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from '@/composables/useToast';
import Loading from '@/components/common/Loading.vue';
import Modal from '@/components/common/Modal.vue';
import Navbar from '@/components/common/Navbar.vue';
import KnowledgeGraph from '@/components/knowledge/KnowledgeGraphEcharts.vue';
import { searchKnowledge, getRecommendedKnowledge } from '@/api/knowledge';

const router = useRouter();
const { showToast } = useToast();

// 视图切换
const currentView = ref<'search' | 'graph'>('search');

// 搜索视图相关
const searchKeyword = ref('');
const selectedType = ref('all');
const loading = ref(false);
const hasSearched = ref(false);
const searchResults = ref<any[]>([]);
const showDetailModal = ref(false);
const selectedItem = ref<any>(null);

// 图谱视图相关
const graphSearchKeyword = ref('');
const graphEntityName = ref('');
const graphEntityType = ref<string | undefined>(undefined);
const graphExamples = ['糖尿病', '高血压', '感冒', '阿司匹林', '头痛'];

// 推荐知识（页面加载时显示）
const recommendedKnowledge = ref<any[]>([]);

// 默认展示的热门内容
const popularDiseases = ref([
  { name: '感冒', type: 'Disease', description: '感冒是由病毒引起的上呼吸道感染，常见症状包括鼻塞、流涕、咳嗽、发热等。' },
  { name: '高血压', type: 'Disease', description: '高血压是指血压持续高于正常值的慢性疾病，可能导致心脑血管并发症。' },
  { name: '糖尿病', type: 'Disease', description: '糖尿病是一种代谢性疾病，特征是血糖水平持续升高。' },
  { name: '冠心病', type: 'Disease', description: '冠状动脉粥样硬化性心脏病，是冠状动脉血管发生动脉粥样硬化病变。' }
]);

const popularSymptoms = ref([
  { name: '头痛', type: 'Symptom', description: '头部疼痛，可能由多种原因引起，如紧张、感冒、高血压等。' },
  { name: '发热', type: 'Symptom', description: '体温升高超过正常范围，通常指腋温超过37.3℃。' },
  { name: '咳嗽', type: 'Symptom', description: '呼吸道受刺激时的保护性反射动作。' },
  { name: '胸闷', type: 'Symptom', description: '胸部有压迫感或呼吸不畅的感觉。' }
]);

const popularDrugs = ref([
  { name: '阿司匹林', type: 'Drug', description: '非甾体抗炎药，用于解热镇痛，预防心脑血管疾病。' },
  { name: '布洛芬', type: 'Drug', description: '非甾体抗炎药，用于解热镇痛，缓解轻至中度疼痛。' },
  { name: '头孢克肟', type: 'Drug', description: '第三代头孢菌素类抗生素，用于治疗细菌感染。' }
]);

const entityTypes = [
  { label: '全部', value: 'all' },
  { label: '疾病', value: 'disease' },
  { label: '症状', value: 'symptom' },
  { label: '药品', value: 'drug' },
  { label: '检查', value: 'check' }
];

const examples = [
  '感冒', '发烧', '头痛', '高血压', '糖尿病',
  '阿司匹林', '血常规', '咳嗽', '胃痛'
];

const selectType = (type: string) => {
  selectedType.value = type;
  if (hasSearched.value) {
    handleSearch();
  }
};

const getTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    'Disease': '疾病',
    'Symptom': '症状',
    'Drug': '药品',
    'Check': '检查',
    'Department': '科室'
  };
  return typeMap[type] || type;
};

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    showToast('请输入搜索关键词', 'warning');
    return;
  }

  loading.value = true;
  hasSearched.value = true;

  try {
    // 调用后端搜索API，请求最多100条结果
    const response = await searchKnowledge(
      searchKeyword.value,
      selectedType.value,
      100
    );
    
    if (response.status === 'success') {
      searchResults.value = response.results || [];
      if (searchResults.value.length === 0) {
        showToast('未找到相关结果', 'info');
      }
    } else {
      showToast(response.message || '搜索失败', 'error');
      searchResults.value = [];
    }
  } catch (error) {
    console.error('搜索失败:', error);
    showToast('搜索失败，请稍后重试', 'error');
    searchResults.value = [];
  } finally {
    loading.value = false;
  }
};

const searchExample = (keyword: string) => {
  searchKeyword.value = keyword;
  handleSearch();
};

const viewDetail = (item: any) => {
  selectedItem.value = item;
  showDetailModal.value = true;
};

const askAbout = (name: string) => {
  showDetailModal.value = false;
  router.push({ 
    name: 'Chat', 
    query: { question: `请介绍一下${name}` }
  });
};

// 图谱搜索
const handleGraphSearch = () => {
  if (!graphSearchKeyword.value.trim()) {
    showToast('请输入实体名称', 'warning');
    return;
  }
  graphEntityName.value = graphSearchKeyword.value.trim();
  graphEntityType.value = undefined;
};

const searchGraph = (keyword: string) => {
  graphSearchKeyword.value = keyword;
  handleGraphSearch();
};

const handleGraphNodeClick = (nodeData: any) => {
  console.log('图谱节点点击:', nodeData);
  // 可以打开详情弹窗或切换到该节点的图谱
  if (nodeData && nodeData.name) {
    graphEntityName.value = nodeData.name;
  }
};

// 加载推荐知识
const loadRecommendedKnowledge = async () => {
  try {
    const response = await getRecommendedKnowledge(9);
    if (response.status === 'success') {
      recommendedKnowledge.value = response.results || [];
    }
  } catch (error) {
    console.error('加载推荐知识失败:', error);
    // 失败时不显示错误，静默处理
  }
};

onMounted(() => {
  loadRecommendedKnowledge();
});
</script>

<style scoped lang="scss">
.knowledge-view {
  width: 100%;
  min-height: 100vh;
  background: #f5f5f5;
}

.knowledge-header {
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

  .view-tabs {
    display: flex;
    gap: 12px;

    .tab-btn {
      padding: 8px 24px;
      background: #f5f5f5;
      border: 2px solid transparent;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.3s;
      font-size: 15px;
      color: #666;

      &:hover {
        background: #e8e8e8;
      }

      &.active {
        background: #667eea;
        color: white;
        border-color: #667eea;
      }
    }
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

.knowledge-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px 20px;
}

.search-view,
.graph-view {
  width: 100%;
}

.graph-view {
  background: white;
  border-radius: 12px;
  padding: 24px;
  min-height: 700px;
  height: calc(100vh - 250px);

  .graph-search {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;

    input {
      flex: 1;
      padding: 14px 20px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      font-size: 16px;
      transition: all 0.3s;

      &:focus {
        outline: none;
        border-color: #667eea;
      }
    }

    .btn-search {
      padding: 14px 32px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 16px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: #5568d3;
      }
    }
  }

  .graph-intro {
    text-align: center;
    padding: 80px 20px;

    .intro-icon {
      font-size: 64px;
      margin-bottom: 20px;
    }

    h3 {
      font-size: 24px;
      color: #333;
      margin-bottom: 12px;
    }

    p {
      font-size: 16px;
      color: #666;
      margin-bottom: 32px;
    }

    .example-searches {
      display: flex;
      justify-content: center;
      gap: 12px;
      flex-wrap: wrap;

      .example-tag {
        padding: 8px 20px;
        background: #f5f5f5;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s;
        font-size: 14px;

        &:hover {
          background: #667eea;
          color: white;
        }
      }
    }
  }
}

.search-section {
  background: white;
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .search-box {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;

    input {
      flex: 1;
      padding: 14px 20px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      font-size: 16px;
      transition: all 0.3s;

      &:focus {
        outline: none;
        border-color: #667eea;
      }
    }

    .btn-search {
      padding: 14px 32px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 16px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: #5568d3;
      }
    }
  }

  .search-filters {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;

    .filter-btn {
      padding: 8px 20px;
      background: #f5f5f5;
      border: 2px solid transparent;
      border-radius: 20px;
      cursor: pointer;
      transition: all 0.3s;
      font-size: 14px;

      &:hover {
        background: #e8e8e8;
      }

      &.active {
        background: #667eea;
        color: white;
        border-color: #667eea;
      }
    }
  }
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 12px;

  .empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
  }

  p {
    font-size: 16px;
    color: #666;
    margin-bottom: 8px;
  }

  .empty-hint {
    font-size: 14px;
    color: #999;
  }
}

.results-section {
  h2 {
    font-size: 24px;
    color: #333;
    margin-bottom: 24px;
  }
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  max-height: calc(100vh - 400px);
  overflow-y: auto;
  padding-right: 8px;

  /* 自定义滚动条样式 */
  &::-webkit-scrollbar {
    width: 8px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;

    &:hover {
      background: #555;
    }
  }
}

.result-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }

  .card-header {
    margin-bottom: 16px;

    .entity-type {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 12px;

      &.disease { background: #e3f2fd; color: #1976d2; }
      &.symptom { background: #fff3e0; color: #f57c00; }
      &.drug { background: #f3e5f5; color: #7b1fa2; }
      &.check { background: #e8f5e9; color: #388e3c; }
    }

    h3 {
      font-size: 20px;
      color: #333;
    }
  }

  .card-body {
    p {
      font-size: 14px;
      color: #666;
      line-height: 1.6;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
  }

  .card-footer {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #f0f0f0;

    .view-detail {
      color: #667eea;
      font-size: 14px;
      font-weight: 500;
    }
  }
}

.intro-section {
  h2 {
    font-size: 28px;
    color: #333;
    margin-bottom: 24px;
    text-align: center;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 48px;
}

.stat-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: 32px;
  text-align: center;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border);
  transition: all var(--transition-base);

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--color-primary);
  }

  .stat-icon {
    margin: 0 auto 16px;
    color: var(--color-primary);
  }

  .stat-value {
    font-size: var(--text-3xl);
    font-weight: var(--font-bold);
    color: var(--color-primary);
    margin-bottom: 8px;
  }

  .stat-label {
    font-size: var(--text-base);
    color: var(--color-text-secondary);
  }
}

.popular-section {
  margin-bottom: 40px;

  h3 {
    font-size: var(--text-xl);
    color: var(--color-text-primary);
    margin-bottom: 20px;
  }
}

.popular-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.popular-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  cursor: pointer;
  transition: all var(--transition-base);

  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    border-color: var(--color-primary);
  }

  .card-header {
    margin-bottom: 12px;

    .entity-type {
      display: inline-block;
      padding: 4px 12px;
      border-radius: var(--radius-full);
      font-size: var(--text-xs);
      font-weight: var(--font-semibold);
      margin-bottom: 8px;

      &.disease { 
        background: rgba(220, 38, 38, 0.1); 
        color: #dc2626; 
      }
      &.symptom { 
        background: rgba(234, 88, 12, 0.1); 
        color: #ea580c; 
      }
      &.drug { 
        background: rgba(124, 58, 237, 0.1); 
        color: #7c3aed; 
      }
    }

    h4 {
      font-size: var(--text-lg);
      color: var(--color-text-primary);
      margin: 0;
    }
  }

  .card-desc {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    line-height: var(--leading-relaxed);
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

.examples-section {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  h3 {
    font-size: 20px;
    color: #333;
    margin-bottom: 20px;
  }

  .example-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;

    .example-tag {
      padding: 8px 20px;
      background: #f5f5f5;
      border-radius: 20px;
      cursor: pointer;
      transition: all 0.3s;
      font-size: 14px;

      &:hover {
        background: #667eea;
        color: white;
      }
    }
  }
}

.detail-content {
  .detail-section {
    margin-bottom: 24px;

    h4 {
      font-size: 18px;
      color: #333;
      margin-bottom: 16px;
    }

    p {
      font-size: 14px;
      color: #666;
      line-height: 1.8;
      margin-bottom: 12px;

      strong {
        color: #333;
      }
    }
  }

  .detail-actions {
    display: flex;
    justify-content: center;
    padding-top: 20px;
    border-top: 1px solid #f0f0f0;

    .btn-ask {
      padding: 12px 32px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 16px;
      transition: all 0.3s;

      &:hover {
        background: #5568d3;
      }
    }
  }
}
</style>
