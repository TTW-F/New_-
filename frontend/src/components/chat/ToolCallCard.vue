<template>
  <div 
    class="tool-call-card"
    :class="[`status-${toolCall.status}`, { 'is-expanded': isExpanded }]"
  >
    <div class="card-header" @click="toggleExpand">
      <div class="header-left">
        <div class="status-icon">
          <IconClock v-if="toolCall.status === 'pending'" :size="16" color="secondary" />
          <IconLoading v-else-if="toolCall.status === 'running'" :size="16" color="primary" />
          <IconCheck v-else-if="toolCall.status === 'success'" :size="16" color="success" />
          <IconError v-else-if="toolCall.status === 'error'" :size="16" color="danger" />
        </div>
        
        <div class="tool-info">
          <span class="tool-name">{{ toolDisplayName }}</span>
          <span class="tool-status">{{ statusText }}</span>
        </div>
      </div>
      
      <button class="expand-button" :aria-label="isExpanded ? '收起' : '展开'">
        <span class="expand-icon" :class="{ 'is-expanded': isExpanded }">▼</span>
      </button>
    </div>
    
    <div v-if="isExpanded" class="card-body">
      <!-- 参数 -->
      <div v-if="Object.keys(toolCall.arguments).length > 0" class="section">
        <h4 class="section-title">调用参数</h4>
        <pre class="code-block">{{ JSON.stringify(toolCall.arguments, null, 2) }}</pre>
      </div>
      
      <!-- 结果 -->
      <div v-if="toolCall.result" class="section">
        <h4 class="section-title">执行结果</h4>
        <div class="result-content">
          <component 
            :is="resultComponent" 
            :data="parsedResult"
            :tool-name="toolCall.tool_name"
          />
        </div>
      </div>
      
      <!-- 错误 -->
      <div v-if="toolCall.error" class="section error-section">
        <h4 class="section-title">错误信息</h4>
        <p class="error-message">{{ toolCall.error }}</p>
      </div>
      
      <!-- 实体 -->
      <div v-if="toolCall.entities && toolCall.entities.length > 0" class="section">
        <h4 class="section-title">识别的实体</h4>
        <div class="entities-list">
          <span 
            v-for="(entity, index) in toolCall.entities" 
            :key="index"
            class="entity-tag"
            :class="`entity-${entity.type.toLowerCase()}`"
          >
            {{ entity.name }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { ToolCall } from '@/types/chat';
import DiseaseCard from '@/components/renderers/DiseaseCard.vue';
import DrugCard from '@/components/renderers/DrugCard.vue';
import TreatmentPlan from '@/components/renderers/TreatmentPlan.vue';
import IconClock from '@/components/icons/IconClock.vue';
import IconLoading from '@/components/icons/IconLoading.vue';
import IconCheck from '@/components/icons/IconCheck.vue';
import IconError from '@/components/icons/IconError.vue';

interface Props {
  toolCall: ToolCall;
}

const props = defineProps<Props>();
const isExpanded = ref(false);

const toolDisplayName = computed(() => {
  const nameMap: Record<string, string> = {
    'diagnose_by_symptoms': '症状诊断',
    'search_disease_info': '疾病查询',
    'get_treatment_plan': '治疗方案',
    'search_drugs': '药品查询',
    'fuzzy_search': '模糊搜索'
  };
  return nameMap[props.toolCall.tool_name] || props.toolCall.tool_name;
});

const statusText = computed(() => {
  const statusMap: Record<string, string> = {
    'pending': '等待中',
    'running': '执行中',
    'success': '成功',
    'error': '失败'
  };
  return statusMap[props.toolCall.status] || props.toolCall.status;
});

const parsedResult = computed(() => {
  if (!props.toolCall.result) return null;
  
  try {
    return JSON.parse(props.toolCall.result);
  } catch {
    return { text: props.toolCall.result };
  }
});

const resultComponent = computed(() => {
  const toolName = props.toolCall.tool_name;
  
  if (toolName === 'diagnose_by_symptoms' || toolName === 'search_disease_info') {
    return DiseaseCard;
  } else if (toolName === 'search_drugs') {
    return DrugCard;
  } else if (toolName === 'get_treatment_plan') {
    return TreatmentPlan;
  }
  
  // 默认显示 JSON
  return 'pre';
});

function toggleExpand() {
  isExpanded.value = !isExpanded.value;
}
</script>

<style scoped lang="scss">
.tool-call-card {
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  background-color: var(--color-bg-primary);
  overflow: hidden;
  transition: all var(--transition-base);
  
  &.status-pending {
    border-color: var(--color-tool-pending);
  }
  
  &.status-running {
    border-color: var(--color-tool-running);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  &.status-success {
    border-color: var(--color-tool-success);
  }
  
  &.status-error {
    border-color: var(--color-tool-error);
  }
  
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-md);
    cursor: pointer;
    user-select: none;
    transition: background-color var(--transition-fast);
    
    &:hover {
      background-color: var(--color-bg-hover);
    }
    
    .header-left {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      
      .status-icon {
        font-size: 1.5rem;
        
        .pulse {
          display: inline-block;
          animation: pulse 2s ease-in-out infinite;
        }
      }
      
      .tool-info {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-xs);
        
        .tool-name {
          font-size: var(--text-base);
          font-weight: var(--font-semibold);
          color: var(--color-text-primary);
        }
        
        .tool-status {
          font-size: var(--text-sm);
          color: var(--color-text-secondary);
        }
      }
    }
    
    .expand-button {
      padding: var(--spacing-xs);
      background: none;
      border: none;
      cursor: pointer;
      color: var(--color-text-secondary);
      transition: transform var(--transition-fast);
      
      .expand-icon {
        display: inline-block;
        transition: transform var(--transition-base);
        
        &.is-expanded {
          transform: rotate(180deg);
        }
      }
    }
  }
  
  .card-body {
    padding: var(--spacing-md);
    border-top: 1px solid var(--color-border);
    background-color: var(--color-bg-secondary);
    animation: expandCard var(--transition-base);
    
    .section {
      margin-bottom: var(--spacing-md);
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .section-title {
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--color-text-secondary);
        margin-bottom: var(--spacing-sm);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      
      .code-block {
        background-color: var(--color-bg-tertiary);
        padding: var(--spacing-sm);
        border-radius: var(--radius-sm);
        font-size: var(--text-sm);
        overflow-x: auto;
        border: 1px solid var(--color-border);
      }
      
      .result-content {
        font-size: var(--text-sm);
      }
      
      &.error-section {
        .error-message {
          color: var(--color-error);
          font-size: var(--text-sm);
          padding: var(--spacing-sm);
          background-color: rgba(239, 68, 68, 0.1);
          border-radius: var(--radius-sm);
          border-left: 3px solid var(--color-error);
        }
      }
      
      .entities-list {
        display: flex;
        flex-wrap: wrap;
        gap: var(--spacing-xs);
        
        .entity-tag {
          padding: var(--spacing-xs) var(--spacing-sm);
          border-radius: var(--radius-full);
          font-size: var(--text-xs);
          font-weight: var(--font-medium);
          
          &.entity-disease {
            background-color: rgba(220, 38, 38, 0.1);
            color: var(--color-entity-disease);
          }
          
          &.entity-symptom {
            background-color: rgba(234, 88, 12, 0.1);
            color: var(--color-entity-symptom);
          }
          
          &.entity-drug {
            background-color: rgba(124, 58, 237, 0.1);
            color: var(--color-entity-drug);
          }
          
          &.entity-treatment {
            background-color: rgba(5, 150, 105, 0.1);
            color: var(--color-entity-treatment);
          }
        }
      }
    }
  }
}
</style>
