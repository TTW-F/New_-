<template>
  <div class="chat-view">
    <Navbar />
    <ChatContainer />
  </div>
</template>

<script setup lang="ts">
import ChatContainer from '@/components/chat/ChatContainer.vue';
import Navbar from '@/components/common/Navbar.vue';
</script>

<style scoped lang="scss">
.chat-view {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
