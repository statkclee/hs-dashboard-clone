<script setup>
import { ICONS } from '../lib/icons.js'
const props = defineProps({ name: String, size: { type: [Number, String], default: 18 } })
</script>

<template>
  <svg
    :width="size" :height="size" viewBox="0 0 24 24"
    fill="none" stroke="currentColor" stroke-width="1.7"
    stroke-linecap="round" stroke-linejoin="round" class="ico"
  >
    <path v-for="(d, i) in (ICONS[name] || [])" :key="i" :d="d" />
  </svg>
</template>

<style scoped>
.ico { display: inline-block; vertical-align: -0.18em; }
</style>
