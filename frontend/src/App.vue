<template>
  <div id="app" class="app-container">
    <RouterView />
    <Toast />
    <ConfirmDialog
      v-model="confirmState.visible"
      :title="confirmState.title"
      :message="confirmState.message"
      :description="confirmState.description"
      :type="confirmState.type"
      :confirm-text="confirmState.confirmText"
      :cancel-text="confirmState.cancelText"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import Toast from './components/common/Toast.vue';
import ConfirmDialog from './components/common/ConfirmDialog.vue';
import { useConfirm } from './composables/useConfirm';

const { state: confirmState, handleConfirm, handleCancel } = useConfirm();
</script>

<style scoped lang="scss">
.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
