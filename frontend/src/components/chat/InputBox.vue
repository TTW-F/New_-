<template>
  <div class="input-box">
    <textarea
      ref="textareaRef"
      v-model="message"
      :placeholder="placeholder"
      :disabled="disabled"
      :maxlength="maxLength"
      class="input-textarea"
      @keydown.enter.exact.prevent="handleSubmit"
      @keydown.enter.shift.exact="handleNewLine"
      @input="adjustHeight"
    />
    
    <div class="input-footer">
      <div class="char-count" :class="{ 'is-limit': isNearLimit }">
        {{ message.length }} / {{ maxLength }}
      </div>
      
      <button
        class="submit-button"
        :disabled="disabled || !canSubmit"
        @click="handleSubmit"
        aria-label="发送消息"
      >
        <IconSend :size="20" class="button-icon" />
        <span class="button-text">发送</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import { IconSend } from '@/components/icons';

interface Props {
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

interface Emits {
  (e: 'submit', message: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  placeholder: '输入您的问题...',
  maxLength: 1000
});

const emit = defineEmits<Emits>();

const message = ref('');
const textareaRef = ref<HTMLTextAreaElement | null>(null);

const canSubmit = computed(() => {
  return message.value.trim().length > 0 && message.value.length <= props.maxLength;
});

const isNearLimit = computed(() => {
  return message.value.length > props.maxLength * 0.9;
});

function handleSubmit() {
  if (!canSubmit.value || props.disabled) return;
  
  const trimmedMessage = message.value.trim();
  if (trimmedMessage) {
    emit('submit', trimmedMessage);
    message.value = '';
    resetHeight();
  }
}

function handleNewLine(event: KeyboardEvent) {
  // Shift+Enter 允许换行
  const textarea = event.target as HTMLTextAreaElement;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  
  message.value = message.value.substring(0, start) + '\n' + message.value.substring(end);
  
  nextTick(() => {
    textarea.selectionStart = textarea.selectionEnd = start + 1;
    adjustHeight();
  });
}

function adjustHeight() {
  if (!textareaRef.value) return;
  
  textareaRef.value.style.height = 'auto';
  const newHeight = Math.min(textareaRef.value.scrollHeight, 200);
  textareaRef.value.style.height = `${newHeight}px`;
}

function resetHeight() {
  if (!textareaRef.value) return;
  textareaRef.value.style.height = 'auto';
}
</script>

<style scoped lang="scss">
.input-box {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  
  .input-textarea {
    width: 100%;
    min-height: 60px;
    max-height: 200px;
    padding: var(--spacing-md);
    border: 2px solid var(--color-border);
    border-radius: var(--radius-lg);
    font-family: var(--font-body);
    font-size: var(--text-base);
    line-height: var(--leading-normal);
    resize: none;
    transition: border-color var(--transition-fast);
    
    &:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px var(--color-primary-alpha);
    }
    
    &:disabled {
      background-color: var(--color-bg-tertiary);
      cursor: not-allowed;
      opacity: 0.6;
    }
    
    &::placeholder {
      color: var(--color-text-tertiary);
    }
  }
  
  .input-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    
    .char-count {
      font-size: var(--text-xs);
      color: var(--color-text-tertiary);
      
      &.is-limit {
        color: var(--color-warning);
        font-weight: var(--font-medium);
      }
    }
    
    .submit-button {
      display: flex;
      align-items: center;
      gap: var(--spacing-xs);
      padding: var(--spacing-sm) var(--spacing-lg);
      background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
      color: white;
      border: none;
      border-radius: var(--radius-full);
      font-size: var(--text-base);
      font-weight: var(--font-medium);
      cursor: pointer;
      transition: all var(--transition-fast);
      box-shadow: var(--shadow-md);
      
      &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
      }
      
      &:active:not(:disabled) {
        transform: translateY(0);
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
      }
      
      .button-icon {
        flex-shrink: 0;
      }
      
      .button-text {
        font-family: var(--font-body);
      }
    }
  }
}
</style>
