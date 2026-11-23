<script setup>
defineProps({ rows: Array })
</script>

<template>
  <div class="ev-list">
    <div v-for="(r, i) in rows" :key="i" class="ev">
      <div class="title">{{ r['행사명'] }}</div>
      <div class="sub">{{ r['담당부서'] }} <span class="dot">|</span> {{ r['장소'] }}</div>
    </div>
  </div>
</template>

<style scoped>
.ev-list { display: flex; flex-direction: column; max-height: 420px; overflow-y: auto; }
.ev { padding: 9px 2px; border-bottom: 1px solid var(--rule); }
.ev:last-child { border-bottom: 0; }
.title { color: #fff; font-weight: 700; font-size: .95rem; line-height: 1.3; }
.sub { color: var(--muted); font-size: .82rem; margin-top: 3px; }
.dot { opacity: .5; margin: 0 2px; }
</style>
