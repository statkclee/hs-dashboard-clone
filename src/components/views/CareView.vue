<script setup>
import { ref, onMounted, computed } from 'vue'
import { loadCSV, fmt, num } from '../../lib/data.js'
import Card from '../Card.vue'
import DataTable from '../DataTable.vue'
import StatTile from '../StatTile.vue'

const types = ref([]), dongs = ref([])
onMounted(async () => {
  types.value = await loadCSV('통합돌봄-유형별.csv')
  dongs.value = await loadCSV('통합돌봄-읍면동.csv')
})
const total = computed(() => types.value.reduce((a, r) => a + (num(r['대상자수']) || 0), 0))
const svc = computed(() => types.value.reduce((a, r) => a + (num(r['월평균 서비스건수']) || 0), 0))
const typeCols = computed(() => (types.value[0] ? Object.keys(types.value[0]) : []))
const typeRows = computed(() => types.value.map((r) => typeCols.value.map((c) => r[c])))
const dongCols = computed(() => (dongs.value[0] ? Object.keys(dongs.value[0]) : []))
const dongRows = computed(() => dongs.value.map((r) => dongCols.value.map((c) => r[c])))
</script>

<template>
  <div class="view">
    <div class="synth">⚠ 합성(가상) 데이터 — 개인정보 비수집 원칙에 따라 실제 대상자 행은 수집하지 않고,
      구조·화면 재현용 집계만 생성했습니다. 실데이터는 소관부서 승인·가명처리 후 연결.</div>
    <div class="tiles">
      <StatTile label="돌봄 대상자(합성)" :value="fmt(total) + '명'" icon="family" accent />
      <StatTile label="돌봄 유형" :value="types.length + '종'" icon="clipboard" />
      <StatTile label="월평균 서비스(합성)" :value="fmt(svc) + '건'" icon="briefcase" />
    </div>
    <div class="cols">
      <Card title="돌봄 유형별 현황 (합성)"><DataTable :cols="typeCols" :rows="typeRows" /></Card>
      <Card title="읍면동별 대상자 분포 (합성)"><DataTable :cols="dongCols" :rows="dongRows" /></Card>
    </div>
  </div>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 14px; }
.synth { color: #ffd9b3; background: rgba(236,103,8,.12); border: 1px solid var(--orange);
  border-radius: 8px; padding: .6rem .9rem; font-size: .85rem; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; align-items: start; }
@media (max-width: 1000px) { .cols { grid-template-columns: 1fr; } }
</style>
