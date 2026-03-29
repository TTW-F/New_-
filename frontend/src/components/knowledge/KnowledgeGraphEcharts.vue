<template>
  <div class="knowledge-graph-echarts">
    <!-- 工具栏 -->
    <div class="graph-toolbar">
      <div class="toolbar-left">
        <div class="control-item">
          <label>关系深度:</label>
          <select v-model="depth" @change="loadGraph">
            <option :value="1">1层</option>
            <option :value="2">2层</option>
          </select>
        </div>
        
        <div class="control-item">
          <label>布局:</label>
          <select v-model="layoutType" @change="updateLayout">
            <option value="force">力导向</option>
            <option value="circular">环形</option>
          </select>
        </div>

        <div class="control-item">
          <label>关系筛选:</label>
          <select v-model="relationFilter" @change="filterRelations">
            <option value="all">全部</option>
            <option value="symptom">症状关系</option>
            <option value="drug">药品关系</option>
            <option value="check">检查关系</option>
          </select>
        </div>
      </div>

      <div class="toolbar-right">
        <button @click="resetView" class="btn-tool">
          <span class="icon">🔄</span> 重置
        </button>
        <button @click="zoomIn" class="btn-tool">
          <span class="icon">🔍+</span> 放大
        </button>
        <button @click="zoomOut" class="btn-tool">
          <span class="icon">🔍-</span> 缩小
        </button>
        <button @click="exportImage" class="btn-tool">
          <span class="icon">📷</span> 导出
        </button>
      </div>
    </div>

    <!-- 图谱容器 -->
    <div class="graph-main">
      <div ref="chartRef" class="chart-container"></div>
      
      <!-- 节点信息面板 -->
      <transition name="slide">
        <div v-if="selectedNode" class="node-info-panel">
          <div class="panel-header">
            <h3>{{ selectedNode.name }}</h3>
            <button @click="selectedNode = null" class="btn-close">×</button>
          </div>
          <div class="panel-body">
            <div class="info-item">
              <span class="label">类型:</span>
              <span class="value">{{ getTypeLabel(selectedNode.category) }}</span>
            </div>
            <div v-if="selectedNode.description" class="info-item">
              <span class="label">描述:</span>
              <span class="value">{{ selectedNode.description }}</span>
            </div>
            <div class="info-item">
              <span class="label">关联数:</span>
              <span class="value">{{ selectedNode.connections || 0 }}</span>
            </div>
          </div>
          <div class="panel-footer">
            <button @click="expandNode(selectedNode)" class="btn-action">
              展开关系
            </button>
            <button @click="viewDetail(selectedNode)" class="btn-action">
              查看详情
            </button>
          </div>
        </div>
      </transition>
    </div>

    <!-- 图例 -->
    <div class="graph-legend">
      <div class="legend-title">图例</div>
      <div class="legend-items">
        <div 
          v-for="type in nodeTypes" 
          :key="type.value"
          class="legend-item"
          @click="toggleTypeVisibility(type.value)"
          :class="{ disabled: hiddenTypes.includes(type.value) }"
        >
          <span class="legend-dot" :style="{ background: type.color }"></span>
          <span class="legend-label">{{ type.label }}</span>
        </div>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="graph-stats">
      <div class="stat-item">
        <span class="stat-label">节点:</span>
        <span class="stat-value">{{ visibleNodes.length }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">关系:</span>
        <span class="stat-value">{{ visibleLinks.length }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed, nextTick } from 'vue';
import * as echarts from 'echarts';
import { getEntityGraph } from '@/api/knowledge';
import { useToast } from '@/composables/useToast';

const props = defineProps<{
  entityName: string;
  entityType?: string;
}>();

const emit = defineEmits<{
  nodeClick: [node: any];
}>();

const { showToast } = useToast();

// 图表实例
const chartRef = ref<HTMLElement | null>(null);
let chartInstance: echarts.ECharts | null = null;

// 数据
const depth = ref(1);
const layoutType = ref('force');
const relationFilter = ref('all');
const selectedNode = ref<any>(null);
const hiddenTypes = ref<string[]>([]);

const graphData = ref<{ nodes: any[]; links: any[] }>({
  nodes: [],
  links: []
});

// 节点类型配置
const nodeTypes = [
  { value: 'Disease', label: '疾病', color: '#5470c6' },
  { value: 'Symptom', label: '症状', color: '#ee6666' },
  { value: 'Drug', label: '药品', color: '#9a60b4' },
  { value: 'Check', label: '检查', color: '#3ba272' },
  { value: 'Department', label: '科室', color: '#fc8452' },
  { value: 'Food', label: '食物', color: '#fac858' }
];

// 计算可见节点和连线
const visibleNodes = computed(() => {
  return graphData.value.nodes.filter(node => 
    !hiddenTypes.value.includes(node.category)
  );
});

const visibleLinks = computed(() => {
  const visibleNodeIds = new Set(visibleNodes.value.map(n => n.id));
  let links = graphData.value.links.filter(link => 
    visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target)
  );
  
  // 关系筛选
  if (relationFilter.value !== 'all') {
    links = links.filter(link => {
      const relType = link.name?.toLowerCase() || '';
      return relType.includes(relationFilter.value);
    });
  }
  
  return links;
});

// 获取类型标签
const getTypeLabel = (type: string) => {
  return nodeTypes.find(t => t.value === type)?.label || type;
};

// 获取节点颜色
const getNodeColor = (type: string) => {
  return nodeTypes.find(t => t.value === type)?.color || '#999';
};

// 加载图谱数据
const loadGraph = async () => {
  try {
    const response = await getEntityGraph(props.entityName, props.entityType, depth.value);
    
    if (response.status === 'success') {
      // 转换数据格式
      const nodes = response.nodes.map((node: any, index: number) => {
        const connections = response.links.filter((l: any) => 
          l.from === node.id || l.to === node.id
        ).length;
        
        return {
          id: node.id,
          name: node.text,
          category: node.type,
          symbolSize: node.isCenter ? 80 : Math.max(30, Math.min(60, connections * 8)),
          value: connections,
          description: node.data?.desc || node.data?.description,
          isCenter: node.isCenter,
          connections,
          itemStyle: {
            color: getNodeColor(node.type),
            borderColor: node.isCenter ? '#fff' : getNodeColor(node.type),
            borderWidth: node.isCenter ? 4 : 2,
            shadowBlur: node.isCenter ? 20 : 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)'
          },
          label: {
            show: true,
            fontSize: node.isCenter ? 16 : 12,
            fontWeight: node.isCenter ? 'bold' : 'normal'
          }
        };
      });
      
      const links = response.links.map((link: any) => ({
        source: link.from,
        target: link.to,
        name: link.text,
        lineStyle: {
          color: '#999',
          width: 2,
          curveness: 0.2
        },
        label: {
          show: true,
          formatter: '{c}',
          fontSize: 10
        }
      }));
      
      graphData.value = { nodes, links };
      
      await nextTick();
      renderChart();
    } else {
      showToast(response.message || '加载图谱失败', 'error');
    }
  } catch (error) {
    console.error('加载图谱失败:', error);
    showToast('加载图谱失败', 'error');
  }
};

// 渲染图表
const renderChart = () => {
  if (!chartRef.value) return;
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value);
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `
            <div style="padding: 8px;">
              <strong>${params.data.name}</strong><br/>
              类型: ${getTypeLabel(params.data.category)}<br/>
              关联数: ${params.data.connections}
            </div>
          `;
        } else if (params.dataType === 'edge') {
          return `关系: ${params.data.name}`;
        }
        return '';
      }
    },
    animationDuration: 1000,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        type: 'graph',
        layout: layoutType.value,
        data: visibleNodes.value,
        links: visibleLinks.value,
        roam: true,
        label: {
          show: true,
          position: 'bottom',
          formatter: '{b}'
        },
        edgeLabel: {
          show: true,
          fontSize: 10,
          formatter: '{c}'
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 4
          },
          itemStyle: {
            shadowBlur: 20,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        force: {
          repulsion: 500,
          gravity: 0.1,
          edgeLength: [100, 200],
          layoutAnimation: false,  // 关闭布局动画，避免一直转圈
          friction: 0.6  // 增加摩擦力，让节点更快稳定
        },
        circular: {
          rotateLabel: true
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3
        }
      }
    ]
  };
  
  chartInstance.setOption(option);
  
  // 绑定点击事件
  chartInstance.off('click');
  chartInstance.on('click', (params: any) => {
    if (params.dataType === 'node') {
      selectedNode.value = params.data;
      emit('nodeClick', params.data);
    }
  });
};

// 更新布局
const updateLayout = () => {
  renderChart();
};

// 筛选关系
const filterRelations = () => {
  renderChart();
};

// 切换类型可见性
const toggleTypeVisibility = (type: string) => {
  const index = hiddenTypes.value.indexOf(type);
  if (index > -1) {
    hiddenTypes.value.splice(index, 1);
  } else {
    hiddenTypes.value.push(type);
  }
  renderChart();
};

// 重置视图
const resetView = () => {
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'restore'
    });
  }
};

// 放大
const zoomIn = () => {
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'dataZoom',
      start: 20,
      end: 80
    });
  }
};

// 缩小
const zoomOut = () => {
  if (chartInstance) {
    chartInstance.dispatchAction({
      type: 'dataZoom',
      start: 0,
      end: 100
    });
  }
};

// 导出图片
const exportImage = () => {
  if (chartInstance) {
    const url = chartInstance.getDataURL({
      type: 'png',
      pixelRatio: 2,
      backgroundColor: '#fff'
    });
    const link = document.createElement('a');
    link.download = `${props.entityName}_知识图谱.png`;
    link.href = url;
    link.click();
    showToast('图片导出成功', 'success');
  }
};

// 展开节点
const expandNode = (node: any) => {
  // 这里可以实现动态加载该节点的更多关系
  showToast(`展开 ${node.name} 的关系`, 'info');
};

// 查看详情
const viewDetail = (node: any) => {
  emit('nodeClick', node);
};

// 监听实体变化
watch(() => props.entityName, () => {
  loadGraph();
});

// 监听窗口大小变化
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize();
  }
};

onMounted(() => {
  loadGraph();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped lang="scss">
.knowledge-graph-echarts {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.graph-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  flex-shrink: 0;

  .toolbar-left,
  .toolbar-right {
    display: flex;
    gap: 16px;
    align-items: center;
  }

  .control-item {
    display: flex;
    align-items: center;
    gap: 8px;

    label {
      font-size: 13px;
      font-weight: 500;
    }

    select {
      padding: 6px 12px;
      border: none;
      border-radius: 6px;
      font-size: 13px;
      cursor: pointer;
      background: rgba(255, 255, 255, 0.9);
      
      &:focus {
        outline: none;
        background: white;
      }
    }
  }

  .btn-tool {
    padding: 6px 14px;
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 4px;

    .icon {
      font-size: 14px;
    }

    &:hover {
      background: rgba(255, 255, 255, 0.3);
      border-color: rgba(255, 255, 255, 0.5);
    }
  }
}

.graph-main {
  flex: 1;
  position: relative;
  background: #fafafa;

  .chart-container {
    width: 100%;
    height: 100%;
  }
}

.node-info-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 300px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  z-index: 10;

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }

    .btn-close {
      background: none;
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
      padding: 0;
      width: 24px;
      height: 24px;
      line-height: 1;

      &:hover {
        opacity: 0.8;
      }
    }
  }

  .panel-body {
    padding: 16px 20px;

    .info-item {
      margin-bottom: 12px;
      font-size: 14px;

      .label {
        color: #666;
        margin-right: 8px;
      }

      .value {
        color: #333;
        font-weight: 500;
      }
    }
  }

  .panel-footer {
    display: flex;
    gap: 8px;
    padding: 12px 20px;
    border-top: 1px solid #f0f0f0;

    .btn-action {
      flex: 1;
      padding: 8px 16px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: #5568d3;
      }
    }
  }
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.graph-legend {
  position: absolute;
  bottom: 80px;
  left: 20px;
  background: white;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 5;

  .legend-title {
    font-size: 13px;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
  }

  .legend-items {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: #666;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        color: #333;
      }

      &.disabled {
        opacity: 0.4;
        text-decoration: line-through;
      }

      .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
      }
    }
  }
}

.graph-stats {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: white;
  border-radius: 8px;
  padding: 8px 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 16px;
  z-index: 5;

  .stat-item {
    font-size: 12px;

    .stat-label {
      color: #666;
      margin-right: 4px;
    }

    .stat-value {
      color: #667eea;
      font-weight: 600;
    }
  }
}
</style>
