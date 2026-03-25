<template>
  <div class="drug-card">
    <div v-if="data.drugs && data.drugs.length > 0" class="drugs-list">
      <div 
        v-for="(drug, index) in data.drugs" 
        :key="index"
        class="drug-item"
      >
        <div class="drug-header">
          <h4 class="drug-name">{{ drug.name }}</h4>
          <span v-if="drug.type" class="drug-type">{{ drug.type }}</span>
        </div>
        
        <div v-if="drug.usage" class="drug-info">
          <span class="label">用法用量:</span>
          <span class="highlight">{{ drug.usage }}</span>
        </div>
        
        <div v-if="drug.indications" class="drug-info">
          <span class="label">适应症:</span>
          <span>{{ drug.indications }}</span>
        </div>
        
        <div v-if="drug.contraindications" class="drug-info warning">
          <span class="label">禁忌:</span>
          <span>{{ drug.contraindications }}</span>
        </div>
        
        <div v-if="drug.side_effects" class="drug-info warning">
          <span class="label">副作用:</span>
          <span>{{ drug.side_effects }}</span>
        </div>
        
        <div v-if="drug.precautions" class="drug-info">
          <span class="label">注意事项:</span>
          <span>{{ drug.precautions }}</span>
        </div>
      </div>
    </div>
    
    <div v-else-if="data.name" class="single-drug">
      <h4 class="drug-name">{{ data.name }}</h4>
      
      <div v-if="data.usage" class="drug-info">
        <span class="label">用法用量:</span>
        <span class="highlight">{{ data.usage }}</span>
      </div>
      
      <div v-if="data.indications" class="drug-info">
        <span class="label">适应症:</span>
        <span>{{ data.indications }}</span>
      </div>
      
      <div v-if="data.contraindications" class="drug-info warning">
        <span class="label">禁忌:</span>
        <span>{{ data.contraindications }}</span>
      </div>
    </div>
    
    <pre v-else class="raw-data">{{ JSON.stringify(data, null, 2) }}</pre>
    
    <div class="disclaimer">
      <IconWarning :size="16" color="warning" style="margin-right: 4px; vertical-align: middle;" />
      以上信息仅供参考，具体用药请咨询专业医生或药师。
    </div>
  </div>
</template>

<script setup lang="ts">
import IconWarning from '@/components/icons/IconWarning.vue';

interface Props {
  data: any;
  toolName?: string;
}

defineProps<Props>();
</script>

<style scoped lang="scss">
.drug-card {
  .drugs-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);
    
    .drug-item {
      padding: var(--spacing-md);
      background-color: var(--color-bg-primary);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      border-left: 4px solid var(--color-entity-drug);
      
      .drug-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--spacing-md);
        
        .drug-name {
          font-size: var(--text-lg);
          font-weight: var(--font-semibold);
          color: var(--color-entity-drug);
        }
        
        .drug-type {
          font-size: var(--text-xs);
          font-weight: var(--font-medium);
          color: var(--color-text-secondary);
          background-color: var(--color-bg-tertiary);
          padding: var(--spacing-xs) var(--spacing-sm);
          border-radius: var(--radius-full);
        }
      }
      
      .drug-info {
        margin-bottom: var(--spacing-sm);
        font-size: var(--text-sm);
        line-height: var(--leading-relaxed);
        
        &:last-of-type {
          margin-bottom: 0;
        }
        
        .label {
          font-weight: var(--font-medium);
          color: var(--color-text-secondary);
          margin-right: var(--spacing-xs);
        }
        
        .highlight {
          color: var(--color-entity-drug);
          font-weight: var(--font-medium);
          background-color: rgba(124, 58, 237, 0.1);
          padding: 2px 6px;
          border-radius: var(--radius-sm);
        }
        
        &.warning {
          color: var(--color-warning);
          
          .label {
            color: var(--color-warning);
          }
        }
      }
    }
  }
  
  .single-drug {
    padding: var(--spacing-md);
    background-color: var(--color-bg-primary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    border-left: 4px solid var(--color-entity-drug);
    margin-bottom: var(--spacing-md);
    
    .drug-name {
      font-size: var(--text-lg);
      font-weight: var(--font-semibold);
      color: var(--color-entity-drug);
      margin-bottom: var(--spacing-md);
    }
    
    .drug-info {
      margin-bottom: var(--spacing-sm);
      font-size: var(--text-sm);
      line-height: var(--leading-relaxed);
      
      .label {
        font-weight: var(--font-medium);
        color: var(--color-text-secondary);
        margin-right: var(--spacing-xs);
      }
      
      .highlight {
        color: var(--color-entity-drug);
        font-weight: var(--font-medium);
        background-color: rgba(124, 58, 237, 0.1);
        padding: 2px 6px;
        border-radius: var(--radius-sm);
      }
      
      &.warning {
        color: var(--color-warning);
        
        .label {
          color: var(--color-warning);
        }
      }
    }
  }
  
  .raw-data {
    font-size: var(--text-xs);
    background-color: var(--color-bg-tertiary);
    padding: var(--spacing-sm);
    border-radius: var(--radius-sm);
    overflow-x: auto;
    margin-bottom: var(--spacing-md);
  }
  
  .disclaimer {
    font-size: var(--text-xs);
    color: var(--color-warning);
    background-color: rgba(245, 158, 11, 0.1);
    padding: var(--spacing-sm);
    border-radius: var(--radius-sm);
    border-left: 3px solid var(--color-warning);
  }
}
</style>
