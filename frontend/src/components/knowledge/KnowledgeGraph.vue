<template>
  <div class="knowledge-graph">
    <div class="graph-controls">
      <div class="control-group">
        <label>关系深度:</label>
        <select v-model="depth" @change="loadGraph">
          <option :value="1">1层(直接关系)</option>
          <option :value="2">2层(间接关系)</option>
        </select>
      </div>
      <div class="control-group">
        <button @click="resetView" class="btn-control">重置视图</button>
        <button @click="exportImage" class="btn-control">导出图片</button>
      </div>
    </div>

    <div class="graph-container" ref="graphContainer">
      <div v-if="graphData.nodes.length > 0" style="width: 100%; height: 100%;">
        <RelationGraph
          ref="graphRef"
          :options="graphOptions"
          :on-node-click="onNodeClick"
          :on-line-click="onLineClick"
        />
      </div>
      <div v-else class="empty-graph">
        <p>暂无图谱数据</p>
      </div>
    </div>

    <div class="graph-legend">
      <h4>图例</h4>
      <div class="legend-items">
        <div class="legend-item">
          <span class="legend-color disease"></span>
          <span>疾病</span>
        </div>
        <div class="legend-item">
          <span class="legend-color symptom"></span>
          <span>症状</span>
        </div>
        <div class="legend-item">
          <span class="legend-color drug"></span>
          <span>药品</span>
        </div>
        <div class="legend-item">
          <span class="legend-color check"></span>
          <span>检查</span>
        </div>
        <div class="legend-item">
          <span class="legend-color other"></span>
          <span>其他</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue';
import RelationGraph from 'relation-graph-vue3';
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

const graphRef = ref<any>(null);
const graphContainer = ref<HTMLElement | null>(null);
const depth = ref(1);
const graphData = ref<{ nodes: any[]; links: any[] }>({
  nodes: [],
  links: []
});

// 图谱配置
const graphOptions = ref({
  defaultJunctionPoint: 'border',
  defaultNodeShape: 1,
  defaultNodeWidth: 100,
  defaultNodeHeight: 60,
  defaultLineShape: 1,
  defaultLineColor: '#999',
  defaultNodeBorderWidth: 2,
  defaultNodeColor: '#fff',
  // 使用中心布局
  layout: {
    layoutName: 'center',
    layoutLabel: '中心布局',
    centerOffset_x: 0,
    centerOffset_y: 0,
    distance_coefficient: 1.2,  // 增加节点间距
    min_per_width: 150,
    min_per_height: 150
  },
  defaultExpandHolderPosition: 'right',
  // 允许缩放和拖拽
  allowShowMiniToolBar: true,
  allowShowMiniView: false,
  allowShowMiniNameFilter: false,
  // 自动布局后居中
  moveToCenterWhenRefresh: true,
  zoomToFitWhenRefresh: true
});

// 节点颜色映射
const getNodeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    'Disease': '#e3f2fd',
    'Symptom': '#fff3e0',
    'Drug': '#f3e5f5',
    'Check': '#e8f5e9',
    'Department': '#fce4ec',
    'Food': '#fff9c4'
  };
  return colorMap[type] || '#f5f5f5';
};

const getBorderColor = (type: string) => {
  const colorMap: Record<string, string> = {
    'Disease': '#1976d2',
    'Symptom': '#f57c00',
    'Drug': '#7b1fa2',
    'Check': '#388e3c',
    'Department': '#c2185b',
    'Food': '#fbc02d'
  };
  return colorMap[type] || '#999';
};

// 加载图谱数据
const loadGraph = async () => {
  try {
    const response = await getEntityGraph(props.entityName, props.entityType, depth.value);
    
    if (response.status === 'success') {
      // 转换数据格式
      const nodes = response.nodes.map((node: any) => ({
        id: node.id,
        text: node.text,
        nodeShape: node.isCenter ? 0 : 1,  // 中心节点圆形,其他矩形
        width: node.isCenter ? 140 : 110,
        height: node.isCenter ? 140 : 70,
        color: getNodeColor(node.type),
        borderColor: getBorderColor(node.type),
        borderWidth: node.isCenter ? 4 : 2,
        fontColor: '#333',
        fontSize: node.isCenter ? 18 : 14,
        fontWeight: node.isCenter ? 'bold' : 'normal',
        data: node.data
      }));
      
      const links = response.links.map((link: any) => ({
        from: link.from,
        to: link.to,
        text: link.text,
        color: '#999',
        fontColor: '#666',
        fontSize: 11,
        lineWidth: 2
      }));
      
      graphData.value = { nodes, links };
      
      // 等待 DOM 更新后渲染图谱
      await nextTick();
      if (graphRef.value) {
        graphRef.value.setJsonData(graphData.value, (graphInstance: any) => {
          console.log('图谱渲染完成');
          // 渲染完成后自动调整视图
          setTimeout(() => {
            graphInstance.zoomToFit();
          }, 100);
        });
      }
    } else {
      showToast(response.message || '加载图谱失败', 'error');
    }
  } catch (error) {
    console.error('加载图谱失败:', error);
    showToast('加载图谱失败', 'error');
  }
};

// 节点点击事件
const onNodeClick = (nodeObject: any, event: any) => {
  console.log('节点点击:', nodeObject);
  emit('nodeClick', nodeObject.data);
};

// 连线点击事件
const onLineClick = (lineObject: any, event: any) => {
  console.log('连线点击:', lineObject);
};

// 重置视图
const resetView = () => {
  if (graphRef.value) {
    const graphInstance = graphRef.value.getInstance();
    graphInstance.moveToCenter();
    graphInstance.zoomToFit();
  }
};

// 导出图片
const exportImage = () => {
  if (graphRef.value) {
    const graphInstance = graphRef.value.getInstance();
    graphInstance.exportAsImage(`${props.entityName}_知识图谱.png`);
    showToast('图片导出成功', 'success');
  }
};

// 监听实体变化
watch(() => props.entityName, () => {
  loadGraph();
});

onMounted(() => {
  loadGraph();
});
</script>

<style scoped lang="scss">
.knowledge-graph {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.graph-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;

  .control-group {
    display: flex;
    align-items: center;
    gap: 12px;

    label {
      font-size: 14px;
      color: #666;
      font-weight: 500;
    }

    select {
      padding: 6px 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 14px;
      cursor: pointer;
      
      &:focus {
        outline: none;
        border-color: #667eea;
      }
    }

    .btn-control {
      padding: 6px 16px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: #5568d3;
      }
    }
  }
}

.graph-container {
  flex: 1;
  position: relative;
  min-height: 600px;
  height: 600px;
  overflow: hidden;
  background: #fafafa;

  :deep(.rel-map) {
    width: 100% !important;
    height: 100% !important;
  }

  :deep(.rel-map-canvas) {
    width: 100% !important;
    height: 100% !important;
  }

  .empty-graph {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #999;
    font-size: 16px;
  }
}

.graph-legend {
  padding: 16px 20px;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
  flex-shrink: 0;

  h4 {
    font-size: 14px;
    color: #333;
    margin-bottom: 12px;
  }

  .legend-items {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;

    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: #666;

      .legend-color {
        width: 20px;
        height: 20px;
        border-radius: 4px;
        border: 2px solid;

        &.disease {
          background: #e3f2fd;
          border-color: #1976d2;
        }

        &.symptom {
          background: #fff3e0;
          border-color: #f57c00;
        }

        &.drug {
          background: #f3e5f5;
          border-color: #7b1fa2;
        }

        &.check {
          background: #e8f5e9;
          border-color: #388e3c;
        }

        &.other {
          background: #f5f5f5;
          border-color: #999;
        }
      }
    }
  }
}
</style>
