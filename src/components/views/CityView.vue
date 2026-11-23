<script setup>
import { ref, onMounted, computed } from 'vue'
import { loadJSON, fmt } from '../../lib/data.js'
import Card from '../Card.vue'
import DataTable from '../DataTable.vue'
import StatTile from '../StatTile.vue'

const pop = ref({})
onMounted(async () => { pop.value = await loadJSON('population') })
const ok = computed(() => pop.value?.status === 'ok')
const rows = computed(() =>
  ok.value
    ? [...pop.value.dongs].sort((a, b) => b.total - a.total).map((d) => [d.dong, fmt(d.total)])
    : [])
</script>

<template>
  <div class="view">
    <div class="tiles">
      <StatTile label="주민등록 인구" :value="ok ? fmt(pop.total) + '명' : '— (수집 대기)'" icon="family" accent />
      <StatTile label="읍면동" :value="ok ? pop.n + '곳' : '—'" icon="pin" />
    </div>
    <Card :title="`읍면동별 인구 — ${pop.month || ''} 기준 (주민등록 내국인)`">
      <DataTable :cols="['읍면동', '인구']" :rows="rows" />
    </Card>
  </div>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 14px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
</style>
