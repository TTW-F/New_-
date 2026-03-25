<template>
  <span
    class="entity-highlight"
    :class="`entity-highlight--${entity.type}`"
    :title="`${entityTypeLabel}: ${entity.text}`"
  >
    {{ entity.text }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Entity } from '@/types/chat';

interface Props {
  entity: Entity;
}

const props = defineProps<Props>();

const entityTypeLabel = computed(() => {
  const labels: Record<string, string> = {
    disease: '疾病',
    symptom: '症状',
    drug: '药物',
    treatment: '治疗方案',
    department: '科室'
  };
  return labels[props.entity.type] || props.entity.type;
});
</script>

<style scoped lang="scss">
.entity-highlight {
  display: inline;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-weight: var(--font-medium);
  transition: all var(--transition-fast);
  cursor: help;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: var(--radius-sm);
    opacity: 0;
    transition: opacity var(--transition-fast);
  }
  
  &:hover::before {
    opacity: 1;
    animation: glow 1.5s ease-in-out infinite;
  }
  
  &--disease {
    background-color: var(--color-entity-disease-light);
    color: var(--color-entity-disease);
    
    &::before {
      box-shadow: 0 0 12px var(--color-entity-disease);
    }
  }
  
  &--symptom {
    background-color: var(--color-entity-symptom-light);
    color: var(--color-entity-symptom);
    
    &::before {
      box-shadow: 0 0 12px var(--color-entity-symptom);
    }
  }
  
  &--drug {
    background-color: var(--color-entity-drug-light);
    color: var(--color-entity-drug);
    
    &::before {
      box-shadow: 0 0 12px var(--color-entity-drug);
    }
  }
  
  &--treatment {
    background-color: var(--color-entity-treatment-light);
    color: var(--color-entity-treatment);
    
    &::before {
      box-shadow: 0 0 12px var(--color-entity-treatment);
    }
  }
  
  &--department {
    background-color: var(--color-entity-department-light);
    color: var(--color-entity-department);
    
    &::before {
      box-shadow: 0 0 12px var(--color-entity-department);
    }
  }
}

@keyframes glow {
  0%, 100% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
}
</style>
