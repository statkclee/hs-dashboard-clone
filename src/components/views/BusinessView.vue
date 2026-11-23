<script setup>
import { ref, onMounted, computed } from 'vue'
import { loadCSV } from '../../lib/data.js'
import Card from '../Card.vue'
import DataTable from '../DataTable.vue'
import StatTile from '../StatTile.vue'

const summary = ref([]), cat = ref([])
onMounted(async () => {
  summary.value = await loadCSV('공약사업-요약.csv')
  cat.value = await loadCSV('공약사업-분야별.csv')
})
const val = (k) => (summary.value.find((r) => r['항목'] === k) || {})['값'] || '—'
const catCols = computed(() => (cat.value[0] ? Object.keys(cat.value[0]) : []))
const catRows = computed(() => cat.value.map((r) => catCols.value.map((c) => r[c])))
</script>

<template>
  <div class="view">
    <div class="tiles">
      <StatTile label="전체 공약 수" :value="val('전체 공약 수') + '개'" icon="clipboard" accent />
      <StatTile label="이행 완료" :value="val('이행 완료') + '개'" icon="chart-line" />
      <StatTile label="이행률" :value="val('이행률')" icon="chart-column" />
    </div>
    <Card title="공약사업 — 분야별 추진 현황 (민선8기)">
      <DataTable :cols="catCols" :rows="catRows" />
    </Card>
  </div>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 14px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
</style>
