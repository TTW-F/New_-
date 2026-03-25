<template>
  <span class="typing-indicator">
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
    <span class="typing-dot"></span>
  </span>
</template>

<script setup lang="ts">
// 打字指示器组件 - 显示三个跳动的点
</script>

<style scoped lang="scss">
.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 4px;
  height: 1em;
  
  .typing-dot {
    width: 6px;
    height: 6px;
    background-color: var(--color-primary);
    border-radius: 50%;
    animation: typingDot 1.4s ease-in-out infinite;
    
    &:nth-child(1) {
      animation-delay: 0s;
    }
    
    &:nth-child(2) {
      animation-delay: 0.2s;
    }
    
    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
}
</style>
