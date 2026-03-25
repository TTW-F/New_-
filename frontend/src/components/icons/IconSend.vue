<template>
  <IconBase v-bind="$attrs">
    <path 
      d="M22 2L11 13" 
      stroke="currentColor" 
      stroke-width="2" 
      stroke-linecap="round" 
      stroke-linejoin="round"
    />
    <path 
      d="M22 2L15 22L11 13L2 9L22 2Z" 
      stroke="currentColor" 
      stroke-width="2" 
      stroke-linecap="round" 
      stroke-linejoin="round"
      fill="none"
    />
  </IconBase>
</template>

<script setup lang="ts">
import IconBase from './IconBase.vue';
</script>
