<template>
  <Modal
    :model-value="modelValue"
    :title="title"
    :show-close="false"
    :close-on-overlay="false"
    :close-on-esc="false"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="confirm-dialog">
      <div class="confirm-dialog__icon" :class="`confirm-dialog__icon--${type}`">
        <svg v-if="type === 'warning'" width="48" height="48" viewBox="0 0 48 48" fill="none">
          <path d="M24 8L8 40H40L24 8Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
          <path d="M24 20V28M24 32V34" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <svg v-else-if="type === 'danger'" width="48" height="48" viewBox="0 0 48 48" fill="none">
          <circle cx="24" cy="24" r="16" stroke="currentColor" stroke-width="2"/>
          <path d="M24 16V26M24 30V32" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <svg v-else-if="type === 'info'" width="48" height="48" viewBox="0 0 48 48" fill="none">
          <circle cx="24" cy="24" r="16" stroke="currentColor" stroke-width="2"/>
          <path d="M24 22V32M24 18V20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <svg v-else width="48" height="48" viewBox="0 0 48 48" fill="none">
          <circle cx="24" cy="24" r="16" stroke="currentColor" stroke-width="2"/>
          <path d="M18 24L22 28L30 20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      
      <div class="confirm-dialog__content">
        <p class="confirm-dialog__message">{{ message }}</p>
        <p v-if="description" class="confirm-dialog__description">{{ description }}</p>
      </div>
    </div>
    
    <template #footer>
      <Button
        variant="secondary"
        @click="handleCancel"
        :disabled="loading"
      >
        {{ cancelText }}
      </Button>
      <Button
        :variant="type === 'danger' ? 'danger' : 'primary'"
        @click="handleConfirm"
        :loading="loading"
        :disabled="loading"
      >
        {{ confirmText }}
      </Button>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Modal from './Modal.vue';
import Button from './Button.vue';

interface Props {
  modelValue: boolean;
  title?: string;
  message: string;
  description?: string;
  type?: 'success' | 'warning' | 'danger' | 'info';
  confirmText?: string;
  cancelText?: string;
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void;
  (e: 'confirm'): void | Promise<void>;
  (e: 'cancel'): void;
}

const props = withDefaults(defineProps<Props>(), {
  title: '确认操作',
  type: 'warning',
  confirmText: '确认',
  cancelText: '取消'
});

const emit = defineEmits<Emits>();

const loading = ref(false);

const handleConfirm = async () => {
  loading.value = true;
  try {
    await emit('confirm');
    emit('update:modelValue', false);
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  emit('cancel');
  emit('update:modelValue', false);
};
</script>

<style scoped lang="scss">
.confirm-dialog {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg) 0;
  
  &__icon {
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-full);
    
    &--success {
      color: var(--color-success);
      background-color: rgba(34, 197, 94, 0.1);
    }
    
    &--warning {
      color: var(--color-warning);
      background-color: rgba(251, 146, 60, 0.1);
    }
    
    &--danger {
      color: var(--color-danger);
      background-color: rgba(239, 68, 68, 0.1);
    }
    
    &--info {
      color: var(--color-primary);
      background-color: rgba(59, 130, 246, 0.1);
    }
  }
  
  &__content {
    text-align: center;
    max-width: 400px;
  }
  
  &__message {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: var(--color-text-primary);
    margin: 0 0 var(--spacing-sm) 0;
  }
  
  &__description {
    font-size: var(--text-sm);
    color: var(--color-text-secondary);
    line-height: var(--leading-relaxed);
    margin: 0;
  }
}
</style>
