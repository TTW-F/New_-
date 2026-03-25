<template>
  <IconBase :size="size" :color="color" class="icon-loading">
    <circle
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      fill="none"
      opacity="0.25"
    />
    <path
      d="M12 2a10 10 0 0 1 10 10"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      fill="none"
    />
  </IconBase>
</template>

<script setup lang="ts">
import IconBase from './IconBase.vue'

interface Props {
  size?: number | string
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'secondary' | 'current'
}

withDefaults(defineProps<Props>(), {
  size: 20,
  color: 'primary'
})
</script>

<style scoped lang="scss">
.icon-loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
