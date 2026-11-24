<script setup>
import { ref } from 'vue'
import Icon from './Icon.vue'
const props = defineProps({
  icon: { type: String, default: 'house' },
  title: String,
  items: { type: Array, default: () => [] }, // [{label, key}]
  modelValue: String,
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="menu-wrap">
    <aside class="side">
      <div class="side-head">
        <div class="side-ic"><Icon :name="icon" :size="40" /></div>
        <div class="side-title">{{ title }}</div>
      </div>
      <nav class="side-nav">
        <a
          v-for="it in items" :key="it.key" href="#"
          class="side-item" :class="{ on: modelValue === it.key }"
          @click.prevent="emit('update:modelValue', it.key)"
        >{{ it.label }}</a>
      </nav>
    </aside>
    <main class="menu-main"><slot /></main>
  </div>
</template>

<style scoped>
.menu-wrap { display: grid; grid-template-columns: 190px 1fr; gap: 16px; align-items: start; }
.side { position: sticky; top: 72px; padding: 8px 4px; }
.side-head { text-align: center; padding: 12px 0 16px; }
.side-ic { color: #cfe0f5; opacity: .9; }
.side-title { color: #fff; font-weight: 800; font-size: 1.25rem; margin-top: 10px; letter-spacing: -.01em; }
.side-nav { display: flex; flex-direction: column; gap: 2px; border-top: 1px solid var(--rule); padding-top: 10px; }
.side-item { color: var(--muted); text-decoration: none; padding: 9px 12px; border-radius: 7px; font-size: .95rem; }
.side-item:hover { color: #fff; background: rgba(255,255,255,.05); }
.side-item.on { color: #fff; font-weight: 700; border-left: 3px solid var(--orange-hot); background: rgba(255,120,24,.08); }
.menu-main { min-width: 0; display: flex; flex-direction: column; gap: 16px; }
@media (max-width: 900px) {
  .menu-wrap { grid-template-columns: 1fr; }
  .side { position: static; display: flex; align-items: center; gap: 16px; }
  .side-head { display: flex; align-items: center; gap: 10px; padding: 8px 0; }
  .side-title { margin: 0; font-size: 1.1rem; }
  .side-nav { flex-direction: row; flex-wrap: wrap; border-top: 0; padding-top: 0; }
}
</style>
