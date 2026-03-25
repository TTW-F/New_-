<template>
  <IconBase v-bind="$attrs">
    <path 
      d="M12 2C13.1046 2 14 2.89543 14 4V5H16C17.1046 5 18 5.89543 18 7V9H20C20.5523 9 21 9.44772 21 10V14C21 14.5523 20.5523 15 20 15H18V19C18 20.1046 17.1046 21 16 21H8C6.89543 21 6 20.1046 6 19V15H4C3.44772 15 3 14.5523 3 14V10C3 9.44772 3.44772 9 4 9H6V7C6 5.89543 6.89543 5 8 5H10V4C10 2.89543 10.8954 2 12 2Z" 
      stroke="currentColor" 
      stroke-width="2" 
      stroke-linecap="round" 
      stroke-linejoin="round"
      fill="none"
    />
    <circle cx="9.5" cy="12" r="1.5" fill="currentColor"/>
    <circle cx="14.5" cy="12" r="1.5" fill="currentColor"/>
    <path 
      d="M9 16H15" 
      stroke="currentColor" 
      stroke-width="2" 
      stroke-linecap="round"
    />
  </IconBase>
</template>

<script setup lang="ts">
import IconBase from './IconBase.vue';
</script>
