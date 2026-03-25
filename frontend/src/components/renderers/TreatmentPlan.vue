<template>
  <div class="treatment-plan">
    <div v-if="data.treatment_plan" class="plan-content">
      <div v-if="Array.isArray(data.treatment_plan)" class="plan-steps">
        <div 
          v-for="(step, index) in data.treatment_plan" 
          :key="index"
          class="plan-step"
        >
          <div class="step-number">{{ (index as number) + 1 }}</div>
          <div class="step-content">
            <h5 v-if="step.title" class="step-title">{{ step.title }}</h5>
            <p class="step-description">{{ step.description || step }}</p>
            
            <div v-if="step.details" class="step-details">
              {{ step.details }}
            </div>
            
            <div v-if="step.duration" class="step-duration">
              <span class="label">疗程:</span>
              <span>{{ step.duration }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="plan-text">
        {{ data.treatment_plan }}
      </div>
    </div>
    
    <div v-else-if="data.steps" class="plan-steps">
      <div 
        v-for="(step, index) in data.steps" 
        :key="index"
        class="plan-step"
      >
        <div class="step-number">{{ (index as number) + 1 }}</div>
        <div class="step-content">
          <p class="step-description">{{ step }}</p>
        </div>
      </div>
    </div>
    
    <pre v-else class="raw-data">{{ JSON.stringify(data, null, 2) }}</pre>
    
    <div v-if="data.precautions || data.notes" class="plan-notes">
      <h5 class="notes-title">注意事项</h5>
      <p class="notes-content">{{ data.precautions || data.notes }}</p>
    </div>
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
.treatment-plan {
  .plan-content {
    margin-bottom: var(--spacing-md);
  }
  
  .plan-steps {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    
    .plan-step {
      display: flex;
      gap: var(--spacing-md);
      padding: var(--spacing-md);
      background-color: var(--color-bg-primary);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-md);
      border-left: 4px solid var(--color-entity-treatment);
      
      .step-number {
        flex-shrink: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: var(--color-entity-treatment);
        color: white;
        border-radius: var(--radius-full);
        font-weight: var(--font-semibold);
        font-size: var(--text-sm);
      }
      
      .step-content {
        flex: 1;
        
        .step-title {
          font-size: var(--text-base);
          font-weight: var(--font-semibold);
          color: var(--color-entity-treatment);
          margin-bottom: var(--spacing-xs);
        }
        
        .step-description {
          font-size: var(--text-sm);
          color: var(--color-text-primary);
          line-height: var(--leading-relaxed);
          margin-bottom: var(--spacing-sm);
        }
        
        .step-details {
          font-size: var(--text-sm);
          color: var(--color-text-secondary);
          line-height: var(--leading-relaxed);
          margin-bottom: var(--spacing-sm);
        }
        
        .step-duration {
          font-size: var(--text-xs);
          color: var(--color-text-secondary);
          
          .label {
            font-weight: var(--font-medium);
            margin-right: var(--spacing-xs);
          }
        }
      }
    }
  }
  
  .plan-text {
    padding: var(--spacing-md);
    background-color: var(--color-bg-primary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    border-left: 4px solid var(--color-entity-treatment);
    font-size: var(--text-sm);
    line-height: var(--leading-relaxed);
    white-space: pre-wrap;
  }
  
  .raw-data {
    font-size: var(--text-xs);
    background-color: var(--color-bg-tertiary);
    padding: var(--spacing-sm);
    border-radius: var(--radius-sm);
    overflow-x: auto;
    margin-bottom: var(--spacing-md);
  }
  
  .plan-notes {
    padding: var(--spacing-md);
    background-color: rgba(59, 130, 246, 0.05);
    border: 1px solid var(--color-primary);
    border-radius: var(--radius-md);
    
    .notes-title {
      font-size: var(--text-sm);
      font-weight: var(--font-semibold);
      color: var(--color-primary);
      margin-bottom: var(--spacing-sm);
    }
    
    .notes-content {
      font-size: var(--text-sm);
      color: var(--color-text-secondary);
      line-height: var(--leading-relaxed);
    }
  }
}
</style>
