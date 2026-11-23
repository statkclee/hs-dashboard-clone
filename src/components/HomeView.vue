<script setup>
import { ref, onMounted, computed } from 'vue'
import { loadJSON, loadCSV, loadGeo } from '../lib/data.js'
import Card from './Card.vue'
import DataTable from './DataTable.vue'
import WeatherMini from './WeatherMini.vue'
import PopCard from './PopCard.vue'
import StatureCards from './StatureCards.vue'
import PopMap from './PopMap.vue'
import WeatherAir from './WeatherAir.vue'
import EventsList from './EventsList.vue'
import TideCard from './TideCard.vue'
import DateBar from './DateBar.vue'

const wx = ref({}), air = ref({}), pop = ref({}), stations = ref({}), geo = ref(null)
const events = ref([]), tide = ref([]), stature = ref([])

onMounted(async () => {
  ;[wx.value, air.value, pop.value, stations.value, geo.value] = await Promise.all([
    loadJSON('weather'), loadJSON('air'), loadJSON('population'), loadJSON('stations'),
    loadGeo('hwaseong_emd.geojson'),
  ])
  ;[events.value, tide.value, stature.value] = await Promise.all([
    loadCSV('행사.csv'), loadCSV('제부도물때.csv'), loadCSV('위상카드-다모아.csv'),
  ])
})

const eventsTop = computed(() => events.value.slice(0, 3)) // 홈은 이달의 행사 3개만
</script>

<template>
  <div class="home">
    <div class="col left">
      <div class="pair">
        <WeatherMini :wx="wx" :air="air" />
        <div class="pop-col">
          <DateBar />
          <PopCard />
        </div>
      </div>
      <div class="pair pair-eq">
        <Card title="이 달의 행사">
          <EventsList :rows="eventsTop" />
        </Card>
        <Card title="제부도 바닷길">
          <TideCard :rows="tide" />
        </Card>
      </div>
      <Card title="화성특례시의 위상">
        <StatureCards :rows="stature" />
      </Card>
    </div>

    <div class="col center">
      <Card title="읍면동 인구 지도 — 공개 행정동 GeoJSON (네이버 키 불필요)" class="mapcard">
        <PopMap :geo="geo" :pop="pop" :stations="stations" />
      </Card>
    </div>

    <div class="col right">
      <WeatherAir :wx="wx" :air="air" />
    </div>
  </div>
</template>

<style scoped>
.home { display: grid; grid-template-columns: minmax(420px, 1.25fr) 1.5fr 1fr; gap: 14px; align-items: start; }
.col { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
/* 좌측 영역: 2열(화성시|인구, 행사|제부도), 위상은 전체폭 */
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; align-items: start; }
.pop-col { display: flex; flex-direction: column; gap: 14px; }
/* 행사|제부도: 패널 높이 동일 — 행사는 내부 스크롤, 제부도는 1차/2차 상하 분배 */
.pair-eq { align-items: stretch; height: 300px; }
.pair-eq > .card { height: 100%; display: flex; flex-direction: column; }
.pair-eq > .card :deep(.card-b) { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.mapcard :deep(.card-b) { padding: 0; }
@media (max-width: 1200px) {
  .home { grid-template-columns: 1fr; }
  .pair { grid-template-columns: 1fr 1fr; }
}
</style>
