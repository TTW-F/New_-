<template>
  <IconBase :size="size" :color="color">
    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" />
    <path
      d="M9 12l2 2 4-4"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
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
  color: 'success'
})
</script>
