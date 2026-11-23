<script setup>
import { ref, onMounted, computed } from 'vue'
import { loadCSV } from '../../lib/data.js'
import Card from '../Card.vue'
import DataTable from '../DataTable.vue'
import EventsList from '../EventsList.vue'
import TideCard from '../TideCard.vue'

const events = ref([]), tide = ref([]), sister = ref([])
onMounted(async () => {
  events.value = await loadCSV('행사.csv')
  tide.value = await loadCSV('제부도물때.csv')
  sister.value = await loadCSV('교류도시.csv')
})
const sisCols = computed(() => (sister.value[0] ? Object.keys(sister.value[0]) : []))
const sisRows = computed(() => sister.value.map((r) => sisCols.value.map((c) => r[c])))
</script>

<template>
  <div class="view">
    <div class="cols">
      <Card title="이 달의 행사"><EventsList :rows="events" /></Card>
      <Card title="제부도 바닷길 물때"><TideCard :rows="tide" /></Card>
    </div>
    <Card title="국제교류도시 · 자매·우호도시">
      <DataTable :cols="sisCols" :rows="sisRows" />
    </Card>
  </div>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 14px; }
.cols { display: grid; grid-template-columns: 1.4fr 1fr; gap: 14px; align-items: start; }
@media (max-width: 1000px) { .cols { grid-template-columns: 1fr; } }
</style>
