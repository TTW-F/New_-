<template>
  <div 
    class="message-item"
    :class="[`message-${message.role}`, { 'is-streaming': isStreaming }]"
  >
    <UserMessage 
      v-if="message.role === 'user'" 
      :message="message"
    />
    
    <AssistantMessage
      v-else-if="message.role === 'assistant'"
      :message="message"
      :is-streaming="isStreaming"
    />
  </div>
</template>

<script setup lang="ts">
import type { Message } from '@/types/chat';
import UserMessage from './UserMessage.vue';
import AssistantMessage from './AssistantMessage.vue';

interface Props {
  message: Message;
  isStreaming: boolean;
}

defineProps<Props>();
</script>

<style scoped lang="scss">
.message-item {
  animation: slideInUp var(--transition-base);
}
</style>
