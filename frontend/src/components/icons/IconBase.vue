<template>
  <svg
    :width="size"
    :height="size"
    :viewBox="`0 0 ${viewBox} ${viewBox}`"
    :class="['icon', `icon--${color}`]"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <slot />
  </svg>
</template>

<script setup lang="ts">
interface Props {
  size?: number | string
  viewBox?: number
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'secondary' | 'current'
}

withDefaults(defineProps<Props>(), {
  size: 24,
  viewBox: 24,
  color: 'current'
})
</script>

<style scoped lang="scss">
.icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
  
  &--primary {
    color: var(--color-primary);
  }
  
  &--success {
    color: var(--color-success);
  }
  
  &--warning {
    color: var(--color-warning);
  }
  
  &--danger {
    color: var(--color-danger);
  }
  
  &--secondary {
    color: var(--color-text-secondary);
  }
  
  &--current {
    color: currentColor;
  }
}
</style>
