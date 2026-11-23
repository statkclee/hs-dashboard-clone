<script setup>
import { ref, onMounted, computed } from 'vue'
import { loadJSON } from '../../lib/data.js'
import Card from '../Card.vue'
import DataTable from '../DataTable.vue'
import StatTile from '../StatTile.vue'

const air = ref({}), ls = ref({})
onMounted(async () => {
  air.value = await loadJSON('air')
  ls.value = await loadJSON('landslide')
})
const airOk = computed(() => air.value?.status === 'ok')
const lsOk = computed(() => ls.value?.status === 'ok')
const airRows = computed(() => (airOk.value ? air.value.stations.map((s) => [s.station, s.pm10, s.pm25, s.o3]) : []))
const lsRows = computed(() => (lsOk.value ? ls.value.items.map((r) => [r['읍면동법정코드'], r['지명'], r['예상피해']]) : []))
</script>

<template>
  <div class="view">
    <div class="tiles">
      <StatTile label="미세먼지(PM10) 평균" :value="airOk ? air.pm10_avg + ' ㎍/㎥' : '— (수집 대기)'" icon="shield" accent />
      <StatTile label="초미세먼지(PM2.5) 평균" :value="airOk ? air.pm25_avg + ' ㎍/㎥' : '—'" icon="shield" />
      <StatTile label="산사태우려지역" :value="lsOk ? ls.n + '곳' : '— (수집 대기)'" icon="pin" />
    </div>
    <div class="cols">
      <Card title="실시간 대기질 — 화성시 측정소">
        <DataTable :cols="['측정소', '미세(PM10)', '초미세(PM2.5)', '오존']" :rows="airRows" />
      </Card>
      <Card title="산사태우려지역 — 화성시 (safetydata)">
        <p v-if="lsOk && !ls.n" class="muted">화성시 산사태우려지역 지정 없음(평지).</p>
        <template v-else>
          <p v-if="lsOk" class="muted small">전국 {{ ls.nationwide }}건 중 화성 {{ ls.n }}곳</p>
          <DataTable :cols="['읍면동법정코드', '지명', '예상피해']" :rows="lsRows" />
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 14px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
.cols { display: grid; grid-template-columns: 1.3fr 1fr; gap: 14px; align-items: start; }
@media (max-width: 1000px) { .cols { grid-template-columns: 1fr; } }
</style>
