<template>
  <div class="disease-card">
    <div v-if="data.possible_diseases && data.possible_diseases.length > 0" class="diseases-list">
      <div 
        v-for="(disease, index) in data.possible_diseases" 
        :key="index"
        class="disease-item"
      >
        <div class="disease-header">
          <h4 class="disease-name">{{ disease.name }}</h4>
          <span v-if="disease.match_score" class="match-score">
            匹配度: {{ (disease.match_score * 100).toFixed(0) }}%
          </span>
        </div>
        
        <div v-if="disease.symptoms" class="disease-symptoms">
          <span class="label">症状:</span>
          <span class="symptoms-text">{{ disease.symptoms.join('、') }}</span>
        </div>
        
        <div v-if="disease.description" class="disease-description">
          {{ disease.description }}
        </div>
      </div>
    </div>
    
    <div v-else-if="data.name" class="single-disease">
      <h4 class="disease-name">{{ data.name }}</h4>
      
      <div v-if="data.description" class="disease-description">
        {{ data.description }}
      </div>
      
      <div v-if="data.symptoms" class="disease-symptoms">
        <span class="label">常见症状:</span>
        <span class="symptoms-text">{{ Array.isArray(data.symptoms) ? data.symptoms.join('、') : data.symptoms }}</span>
      </div>
      
      <div v-if="data.causes" class="disease-info">
        <span class="label">病因:</span>
        <span>{{ data.causes }}</span>
      </div>
      
      <div v-if="data.prevention" class="disease-info">
        <span class="label">预防:</span>
        <span>{{ data.prevention }}</span>
      </div>
    </div>
    
    <pre v-else class="raw-data">{{ JSON.stringify(data, null, 2) }}</pre>
  </div>
</template>

<script setup lang="ts">
interface Props {
  data: any;
  toolName?: string;
}

defineProps<Props>();
</script>

<style scoped lang="scss">
.disease-card {
  .diseases-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    
    .disease-item {
      padding: var(--spacing-md);
      background-color: var(--color-bg-primary);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      border-left: 4px solid var(--color-entity-disease);
      
      .disease-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--spacing-sm);
        
        .disease-name {
          font-size: var(--text-lg);
          font-weight: var(--font-semibold);
          color: var(--color-entity-disease);
        }
        
        .match-score {
          font-size: var(--text-sm);
          font-weight: var(--font-medium);
          color: var(--color-primary);
          background-color: var(--color-primary-alpha);
          padding: var(--spacing-xs) var(--spacing-sm);
          border-radius: var(--radius-full);
        }
      }
      
      .disease-symptoms {
        margin-bottom: var(--spacing-sm);
        font-size: var(--text-sm);
        
        .label {
          font-weight: var(--font-medium);
          color: var(--color-text-secondary);
          margin-right: var(--spacing-xs);
        }
        
        .symptoms-text {
          color: var(--color-entity-symptom);
        }
      }
      
      .disease-description {
        font-size: var(--text-sm);
        color: var(--color-text-secondary);
        line-height: var(--leading-relaxed);
      }
    }
  }
  
  .single-disease {
    padding: var(--spacing-md);
    background-color: var(--color-bg-primary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    border-left: 4px solid var(--color-entity-disease);
    
    .disease-name {
      font-size: var(--text-lg);
      font-weight: var(--font-semibold);
      color: var(--color-entity-disease);
      margin-bottom: var(--spacing-md);
    }
    
    .disease-description {
      margin-bottom: var(--spacing-md);
      font-size: var(--text-sm);
      color: var(--color-text-secondary);
      line-height: var(--leading-relaxed);
    }
    
    .disease-symptoms,
    .disease-info {
      margin-bottom: var(--spacing-sm);
      font-size: var(--text-sm);
      
      .label {
        font-weight: var(--font-medium);
        color: var(--color-text-secondary);
        margin-right: var(--spacing-xs);
      }
    }
    
    .disease-symptoms .symptoms-text {
      color: var(--color-entity-symptom);
    }
  }
  
  .raw-data {
    font-size: var(--text-xs);
    background-color: var(--color-bg-tertiary);
    padding: var(--spacing-sm);
    border-radius: var(--radius-sm);
    overflow-x: auto;
  }
}
</style>
