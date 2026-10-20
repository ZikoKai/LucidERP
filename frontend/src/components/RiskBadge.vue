<script setup lang="ts">
defineProps<{ score: number }>()
</script>
<template><span class="badge" :class="score >= 50 ? 'high' : score > 0 ? 'medium' : 'low'">{{ score }} / 100</span></template>
