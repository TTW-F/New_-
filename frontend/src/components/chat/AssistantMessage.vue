<template>
  <div class="assistant-message">
    <div class="message-avatar">
      <div class="avatar-icon">
        <IconRobot :size="24" />
      </div>
    </div>
    
    <div class="message-content">
      <div class="message-header">
        <span class="message-author">AI 助手</span>
        <span class="message-time">{{ formattedTime }}</span>
      </div>
      
      <!-- 工具调用卡片 -->
      <div v-if="toolCalls.length > 0" class="tool-calls-section">
        <ToolCallCard
          v-for="toolCall in toolCalls"
          :key="toolCall.id"
          :tool-call="toolCall"
        />
      </div>
      
      <!-- 回答内容 -->
      <div class="message-text">
        <MarkdownRenderer 
          v-if="content"
          :content="highlightedContent" 
        />
        
        <TypingIndicator v-if="isStreaming" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Message } from '@/types/chat';
import { formatRelativeTime } from '@/utils/format';
import MarkdownRenderer from '@/components/renderers/MarkdownRenderer.vue';
import ToolCallCard from './ToolCallCard.vue';
import TypingIndicator from './TypingIndicator.vue';
import { IconRobot } from '@/components/icons';

interface Props {
  message: Message;
  isStreaming: boolean;
}

const props = defineProps<Props>();

const content = computed(() => props.message.content);
const toolCalls = computed(() => props.message.toolCalls || []);
const formattedTime = computed(() => formatRelativeTime(props.message.timestamp));

// 实体高亮
const highlightedContent = computed(() => {
  let result = content.value;
  const messageEntities = props.message.entities;
  
  if (messageEntities && messageEntities.length > 0) {
    // 按实体名称长度排序,先处理长的实体名
    const sortedEntities = [...messageEntities].sort((a, b) => 
      b.name.length - a.name.length
    );
    
    for (const entity of sortedEntities) {
      const entityClass = `entity-${entity.type.toLowerCase()}`;
      const regex = new RegExp(`(${entity.name})`, 'g');
      result = result.replace(regex, `<span class="${entityClass}">$1</span>`);
    }
  }
  
  return result;
});
</script>

<style scoped lang="scss">
.assistant-message {
  display: flex;
  gap: var(--spacing-md);
  
  .message-avatar {
    .avatar-icon {
      width: 40px;
      height: 40px;
      border-radius: var(--radius-full);
      background: linear-gradient(135deg, #667eea, #764ba2);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      box-shadow: var(--shadow-md);
    }
  }
  
  .message-content {
    flex: 1;
    max-width: 700px;
    
    .message-header {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      margin-bottom: var(--spacing-xs);
      
      .message-author {
        font-size: var(--text-sm);
        font-weight: var(--font-medium);
        color: var(--color-text-primary);
      }
      
      .message-time {
        font-size: var(--text-xs);
        color: var(--color-text-tertiary);
      }
    }
    
    .tool-calls-section {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
      margin-bottom: var(--spacing-md);
    }
    
    .message-text {
      background-color: var(--color-bg-secondary);
      padding: var(--spacing-md) var(--spacing-lg);
      border-radius: var(--radius-lg);
      border-bottom-left-radius: var(--radius-sm);
      font-size: var(--text-base);
      line-height: var(--leading-relaxed);
      box-shadow: var(--shadow-sm);
      border: 1px solid var(--color-border);
      
      :deep(.entity-disease) {
        color: var(--color-entity-disease);
        font-weight: var(--font-medium);
        padding: 2px 4px;
        border-radius: var(--radius-sm);
        background-color: rgba(220, 38, 38, 0.1);
      }
      
      :deep(.entity-symptom) {
        color: var(--color-entity-symptom);
        font-weight: var(--font-medium);
        padding: 2px 4px;
        border-radius: var(--radius-sm);
        background-color: rgba(234, 88, 12, 0.1);
      }
      
      :deep(.entity-drug) {
        color: var(--color-entity-drug);
        font-weight: var(--font-medium);
        padding: 2px 4px;
        border-radius: var(--radius-sm);
        background-color: rgba(124, 58, 237, 0.1);
      }
      
      :deep(.entity-treatment) {
        color: var(--color-entity-treatment);
        font-weight: var(--font-medium);
        padding: 2px 4px;
        border-radius: var(--radius-sm);
        background-color: rgba(5, 150, 105, 0.1);
      }
    }
  }
}
</style>
