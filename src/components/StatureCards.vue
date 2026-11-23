<script setup>
defineProps({ rows: Array })
</script>

<template>
  <div class="st-grid">
    <div v-for="(r, i) in rows" :key="i" class="st-card">
      <div class="rank">{{ r['순위범위'] }} {{ r['순위'] }}위</div>
      <div class="name">{{ r['지표'] }}</div>
      <div class="val">{{ r['값표기'] }}</div>
    </div>
  </div>
</template>

<style scoped>
.st-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.st-card { background: rgba(255,255,255,.05); border: 1px solid var(--rule);
  border-radius: 8px; padding: 10px 12px; }
.rank { color: var(--orange-hot); font-weight: 800; font-size: .82rem; }
.name { color: var(--muted); font-size: .82rem; margin-top: 2px; }
.val { color: #fff; font-weight: 800; font-size: 1.02rem; margin-top: 3px; letter-spacing: -.01em; }
</style>
