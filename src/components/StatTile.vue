<script setup>
import Icon from './Icon.vue'
defineProps({ label: String, value: String, icon: { type: String, default: 'chart-line' }, accent: Boolean })
</script>

<template>
  <div class="tile" :class="{ accent }">
    <div class="meta">
      <div class="label">{{ label }}</div>
      <div class="value">{{ value }}</div>
    </div>
    <div class="ic"><Icon :name="icon" :size="34" /></div>
  </div>
</template>

<style scoped>
.tile {
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(22,49,78,.82); border: 1px solid var(--rule);
  border-radius: 10px; padding: 16px 18px; box-shadow: 0 8px 24px rgba(0,0,0,.25);
}
.tile.accent { background: linear-gradient(135deg, var(--orange-hot) 0%, var(--orange-hot) 58%, var(--peach) 100%); border-color: transparent; }
.label { color: #c7d6e6; font-size: .9rem; }
.tile.accent .label { color: #fff3ea; }
.value { color: #fff; font-weight: 800; font-size: 1.7rem; letter-spacing: -.02em; margin-top: 4px; }
.ic { color: var(--blue); opacity: .9; }
.tile.accent .ic { color: #fff; opacity: .9; }
</style>
