<template>
  <Teleport to="body">
    <Transition name="modal">
      <div 
        v-if="modelValue"
        class="modal-overlay"
        @click="handleOverlayClick"
        role="dialog"
        aria-modal="true"
      >
        <div 
          class="modal"
          :class="modalClass"
          @click.stop
        >
          <div v-if="showHeader" class="modal__header">
            <h3 class="modal__title">
              <slot name="title">{{ title }}</slot>
            </h3>
            
            <button 
              v-if="showClose"
              class="modal__close"
              @click="handleClose"
              aria-label="关闭"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          
          <div class="modal__body">
            <slot></slot>
          </div>
          
          <div v-if="$slots.footer" class="modal__footer">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue';

interface Props {
  modelValue: boolean;
  title?: string;
  showHeader?: boolean;
  showClose?: boolean;
  closeOnOverlay?: boolean;
  closeOnEsc?: boolean;
  modalClass?: string;
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void;
  (e: 'close'): void;
}

const props = withDefaults(defineProps<Props>(), {
  showHeader: true,
  showClose: true,
  closeOnOverlay: true,
  closeOnEsc: true
});

const emit = defineEmits<Emits>();

const handleClose = () => {
  emit('update:modelValue', false);
  emit('close');
};

const handleOverlayClick = () => {
  if (props.closeOnOverlay) {
    handleClose();
  }
};

const handleEscKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.closeOnEsc && props.modelValue) {
    handleClose();
  }
};

watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});

onMounted(() => {
  document.addEventListener('keydown', handleEscKey);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscKey);
  document.body.style.overflow = '';
});
</script>

<style scoped lang="scss">
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9998;
  padding: var(--spacing-lg);
}

.modal {
  background-color: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  
  &__header {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  &__title {
    font-size: var(--text-lg);
    font-weight: var(--font-semibold);
    color: var(--color-text-primary);
    margin: 0;
  }
  
  &__close {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: none;
    border: none;
    color: var(--color-text-secondary);
    cursor: pointer;
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
    
    &:hover {
      background-color: var(--color-bg-tertiary);
      color: var(--color-text-primary);
    }
  }
  
  &__body {
    padding: var(--spacing-lg);
    overflow-y: auto;
    flex: 1;
  }
  
  &__footer {
    padding: var(--spacing-lg);
    border-top: 1px solid var(--color-border);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: var(--spacing-md);
  }
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--transition-normal);
  
  .modal {
    transition: transform var(--transition-normal);
  }
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  
  .modal {
    transform: scale(0.9) translateY(-20px);
  }
}

@media (max-width: 768px) {
  .modal-overlay {
    padding: 0;
  }
  
  .modal {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
}
</style>
