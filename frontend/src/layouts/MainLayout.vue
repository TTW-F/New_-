<template>
  <div class="main-layout">
    <Navbar />
    <div class="layout-content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import Navbar from '@/components/common/Navbar.vue';
</script>

<style scoped lang="scss">
.main-layout {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-content {
  flex: 1;
  overflow: auto;
}
</style>
