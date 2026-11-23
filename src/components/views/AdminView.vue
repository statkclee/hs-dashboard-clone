<script setup>
import { ref, onMounted, computed } from 'vue'
import { loadCSV } from '../../lib/data.js'
import Card from '../Card.vue'
import DataTable from '../DataTable.vue'
import StatTile from '../StatTile.vue'

const ind = ref([]), aw = ref([])
onMounted(async () => {
  ind.value = await loadCSV('위상지표.csv')
  aw.value = await loadCSV('수상실적.csv')
})
const indRows = computed(() => ind.value.map((r) => [r['지표'], r['값'], r['단위'], r['순위'], r['기준시점']]))
const awRows = computed(() => aw.value.map((r) => [r['연도'], r['수상명'], r['주관기관']]))
</script>

<template>
  <div class="view">
    <div class="tiles">
      <StatTile label="지방자치경쟁력" value="종합 1위" icon="trophy" accent />
      <StatTile label="인구" value="전국 4위" icon="family" />
      <StatTile label="재정·행정 수상" :value="aw.length + '건'" icon="trophy" />
    </div>
    <div class="cols">
      <Card title="화성특례시 위상 지표">
        <DataTable :cols="['지표', '값', '단위', '순위', '기준시점']" :rows="indRows" />
      </Card>
      <Card title="최근 수상·평가 실적">
        <DataTable :cols="['연도', '수상명', '주관기관']" :rows="awRows" />
      </Card>
    </div>
  </div>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 14px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; align-items: start; }
@media (max-width: 1000px) { .cols { grid-template-columns: 1fr; } }
</style>
