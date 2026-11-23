<script setup>
import { computed } from 'vue'
const props = defineProps({ rows: Array })
// 원본: 차수 + [상태]~[시각] 파란 알약. 종료시각이 범위('~')면 시각 두 개로.
const items = computed(() =>
  (props.rows || []).map((r) => {
    const end = String(r['종료시각'] || '')
    const pills = end.includes('~') ? end.split('~').map((s) => s.trim()) : [r['상태'], end]
    return { cha: r['차수'], status: r['상태'], pills }
  }),
)
</script>

<template>
  <div class="tide">
    <div v-for="(it, i) in items" :key="i" class="row">
      <div class="cha">{{ it.cha }}</div>
      <div class="pills">
        <span class="pill">{{ it.pills[0] }}</span>
        <span class="tilde">~</span>
        <span class="pill">{{ it.pills[1] }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tide { display: flex; flex-direction: column; justify-content: space-around; height: 100%; gap: 14px; }
.row { display: flex; flex-direction: column; gap: 10px; }
.cha { font-size: 1.15rem; font-weight: 800; color: #fff; }
.pills { display: flex; align-items: center; gap: 10px; }
.pill {
  background: var(--blue); color: #fff; font-weight: 700; font-size: 1rem;
  padding: 8px 16px; border-radius: 6px; min-width: 70px; text-align: center;
}
.tilde { color: var(--muted); font-weight: 700; }
.row + .row { border-top: 1px solid var(--rule); padding-top: 14px; }
</style>
