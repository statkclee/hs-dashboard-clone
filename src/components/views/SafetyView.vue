<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import L from 'leaflet'
import { loadJSON, loadGeo, airGrade, fmt } from '../../lib/data.js'
import MenuLayout from '../MenuLayout.vue'
import Card from '../Card.vue'
import DataTable from '../DataTable.vue'
import StatTile from '../StatTile.vue'

const items = [
  { label: '대기오염', key: 'air' },
  { label: '산사태', key: 'land' },
  { label: '급경사지', key: 'slope' },
  { label: '교통상황', key: 'traffic' },
  { label: '자전거', key: 'bike' },
]
const active = ref('air')
const air = ref({}), landslide = ref({}), stations = ref({}), geo = ref(null)
const mapEl = ref(null)
let map = null

const airOk = computed(() => air.value?.status === 'ok')
const lsOk = computed(() => landslide.value?.status === 'ok')
const airRows = computed(() =>
  airOk.value ? (air.value.stations || []).map((s) => [s.station, fmt(s.pm10), fmt(s.pm25), s.o3 ?? '—']) : [])
const lsRows = computed(() =>
  lsOk.value ? (landslide.value.items || []).map((r) => [r['읍면동법정코드'], r['지명'], r['예상피해'] ?? '—']) : [])

function destroyMap() {
  if (map) { map.remove(); map = null }
}

async function buildMap() {
  destroyMap()
  await nextTick()
  if (!mapEl.value || !airOk.value) return
  map = L.map(mapEl.value, { center: [37.17, 126.92], zoom: 10, scrollWheelZoom: false })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18, attribution: '&copy; OpenStreetMap',
  }).addTo(map)
  if (geo.value) {
    const layer = L.geoJSON(geo.value, {
      style: { fillColor: '#2c3e50', fillOpacity: 0.25, color: '#ffffff', weight: 1 },
    }).addTo(map)
    try { map.fitBounds(layer.getBounds()) } catch (e) { /* ignore */ }
  }
  const coords = stations.value?.status === 'ok' ? stations.value.stations || [] : []
  for (const s of air.value.stations || []) {
    const c = coords.find((x) => x.station && s.station && (x.station.includes(s.station) || s.station.includes(x.station)))
    if (!c) continue
    const color = airGrade('pm10', s.pm10)[1]
    L.circleMarker([c.lat, c.lng], { radius: 10, color: '#fff', weight: 2, fillColor: color, fillOpacity: 0.9 })
      .bindTooltip(`${s.station} · PM10 ${s.pm10 ?? '—'}`)
      .addTo(map)
  }
  setTimeout(() => map && map.invalidateSize(), 0)
}

onMounted(async () => {
  const [a, l, st, g] = await Promise.all([
    loadJSON('air'), loadJSON('landslide'), loadJSON('stations'), loadGeo('hwaseong_emd.geojson'),
  ])
  air.value = a; landslide.value = l; stations.value = st; geo.value = g
  if (active.value === 'air') await buildMap()
})

watch(active, async (k) => {
  if (k === 'air') await buildMap()
  else destroyMap()
})

onBeforeUnmount(destroyMap)
</script>

<template>
  <MenuLayout icon="shield" title="재난/안전" :items="items" v-model="active">
    <div class="view">
      <!-- 대기오염 -->
      <template v-if="active === 'air'">
        <div class="tiles">
          <StatTile label="미세먼지(PM10) 평균" :value="airOk ? air.pm10_avg + ' ㎍/㎥' : '— (수집 대기)'" icon="shield" accent />
          <StatTile label="초미세먼지(PM2.5) 평균" :value="airOk ? air.pm25_avg + ' ㎍/㎥' : '—'" icon="shield" />
          <StatTile label="측정소 수" :value="airOk ? air.n + '곳' : '—'" icon="pin" />
        </div>
        <Card title="대기오염 지도 — 화성시">
          <div v-if="airOk" ref="mapEl" class="lmap"></div>
          <p v-else class="muted">수집 대기</p>
        </Card>
        <Card title="실시간 대기질 — 측정소">
          <p v-if="!airOk" class="muted">수집 대기</p>
          <DataTable v-else :cols="['측정소', '미세(PM10)', '초미세(PM2.5)', '오존']" :rows="airRows" />
        </Card>
      </template>

      <!-- 산사태 -->
      <template v-else-if="active === 'land'">
        <div class="tiles">
          <StatTile label="산사태우려지역" :value="lsOk ? landslide.n + '곳' : '— (수집 대기)'" icon="pin" accent />
        </div>
        <Card title="산사태우려지역 — 화성시">
          <p v-if="!lsOk" class="muted">수집 대기</p>
          <p v-else-if="!landslide.n" class="muted">화성시 산사태우려지역 지정 없음.</p>
          <DataTable v-else :cols="['읍면동법정코드', '지명', '예상피해']" :rows="lsRows" />
        </Card>
      </template>

      <!-- 급경사지 / 교통상황 / 자전거 -->
      <template v-else>
        <Card :title="items.find((i) => i.key === active)?.label">
          <p class="muted">준비 중</p>
        </Card>
      </template>
    </div>
  </MenuLayout>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; }
.lmap { height: 460px; width: 100%; border-radius: 8px; overflow: hidden; }
.muted { color: var(--muted); margin: 0; }
:deep(.leaflet-container) { background: #0c1b2e; font-family: inherit; }
@media (max-width: 700px) { .lmap { height: 340px; } }
</style>
