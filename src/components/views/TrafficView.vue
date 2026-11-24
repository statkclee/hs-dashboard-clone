<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import L from 'leaflet'
import { loadJSON, loadGeo, fmt } from '../../lib/data.js'
import MenuLayout from '../MenuLayout.vue'
import Card from '../Card.vue'
import DataTable from '../DataTable.vue'
import StatTile from '../StatTile.vue'

const items = [
  { label: '전기차 충전소', key: 'ev' },
  { label: '수소차 충전소', key: 'h2' },
  { label: '주차장', key: 'park' },
]
const active = ref('ev')
const ev = ref(null)
const h2Data = ref([])
const parkData = ref([])
const h2El = ref(null)
const parkEl = ref(null)
let h2Map = null
let parkMap = null
const mapEl = ref(null)
let map = null

const chargers = computed(() => (ev.value?.status === 'ok' && Array.isArray(ev.value.chargers) ? ev.value.chargers : []))
const total = computed(() => ev.value?.n ?? chargers.value.length)
const evRows = computed(() => chargers.value.slice(0, 40).map((c) => [c.name, c.addr, c.connectors]))
const h2Rows = computed(() => h2Data.value.map((s) => [s.nm, s.addr, s.dong]))
const parkRows = computed(() => parkData.value.map((p) => [p.nm, p.addr, p.dong]))
const parkPlot = computed(() => parkData.value.filter((p) => p.lat > 36.9 && p.lat < 37.45 && p.lng > 126.4 && p.lng < 127.4))

function destroyMap() { if (map) { map.remove(); map = null } }

function renderMap() {
  destroyMap()
  if (!mapEl.value || !chargers.value.length) return
  map = L.map(mapEl.value, { scrollWheelZoom: true }).setView([37.2, 126.9], 11)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '© OpenStreetMap' }).addTo(map)
  const pts = []
  chargers.value.forEach((c) => {
    const lat = parseFloat(c.lat), lng = parseFloat(c.lng)
    if (!Number.isFinite(lat) || !Number.isFinite(lng) || !lat || !lng) return
    // 화성시 bounding box 밖(이상 좌표)은 지도에서 제외 — fitBounds 왜곡 방지
    if (lat < 36.9 || lat > 37.45 || lng < 126.5 || lng > 127.35) return
    pts.push([lat, lng])
    L.circleMarker([lat, lng], { radius: 4, color: '#167aff', weight: 1, fillColor: '#2c67df', fillOpacity: 0.75 })
      .bindTooltip(c.name || '충전소').addTo(map)
  })
  if (pts.length) map.fitBounds(pts, { padding: [20, 20] })
  else map.setView([37.2, 126.9], 11)
}

function destroyH2() { if (h2Map) { h2Map.remove(); h2Map = null } }
function destroyPark() { if (parkMap) { parkMap.remove(); parkMap = null } }

function baseMap(el) {
  const m = L.map(el, { scrollWheelZoom: true }).setView([37.2, 126.9], 11)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '© OpenStreetMap' }).addTo(m)
  return m
}

function renderH2() {
  destroyH2()
  if (!h2El.value || !h2Data.value.length) return
  h2Map = baseMap(h2El.value)
  const pts = []
  h2Data.value.forEach((s) => {
    if (!Number.isFinite(s.lat) || !Number.isFinite(s.lng)) return
    pts.push([s.lat, s.lng])
    L.circleMarker([s.lat, s.lng], { radius: 7, color: '#1b9e77', fillColor: '#2fd3a7', fillOpacity: 0.85 })
      .bindTooltip(s.nm || '수소충전소').addTo(h2Map)
  })
  if (pts.length) h2Map.fitBounds(pts, { padding: [30, 30], maxZoom: 13 })
}

function renderPark() {
  destroyPark()
  if (!parkEl.value) return
  parkMap = baseMap(parkEl.value)
  const pts = []
  parkPlot.value.forEach((p) => {
    pts.push([p.lat, p.lng])
    L.circleMarker([p.lat, p.lng], { radius: 4, color: '#167aff', weight: 1, fillColor: '#2c67df', fillOpacity: 0.75 })
      .bindTooltip(p.nm || '주차장').addTo(parkMap)
  })
  if (pts.length) parkMap.fitBounds(pts, { padding: [20, 20] })
  else parkMap.setView([37.2, 126.9], 11)
}

async function buildFor(k) {
  await nextTick()
  if (k === 'ev') renderMap()
  else if (k === 'h2') renderH2()
  else if (k === 'park') renderPark()
}

onMounted(async () => {
  ev.value = await loadJSON('evcharger')
  try { h2Data.value = (await loadGeo('수소충전소.json')) || [] } catch (e) { h2Data.value = [] }
  try { parkData.value = (await loadGeo('주차장.json')) || [] } catch (e) { parkData.value = [] }
  await buildFor(active.value)
})
watch(active, (k) => {
  if (k !== 'ev') destroyMap()
  if (k !== 'h2') destroyH2()
  if (k !== 'park') destroyPark()
  buildFor(k)
})
onBeforeUnmount(() => { destroyMap(); destroyH2(); destroyPark() })
</script>

<template>
  <MenuLayout icon="car" title="교통" :items="items" v-model="active">
          <div class="view" v-if="active === 'ev'">
        <div class="tiles">
          <StatTile label="전기차 충전소" :value="fmt(total) + '곳'" icon="car" accent />
        </div>
        <Card title="전기차 충전소 지도 — 화성시">
          
            <div v-if="ev && !chargers.length" class="muted">서버 수집 대기</div>
            <div ref="mapEl" class="evmap" v-show="chargers.length"></div>
          
        </Card>
        <Card title="충전소 목록">
          
            <DataTable :cols="['충전소', '주소', '충전기수']" :rows="evRows" />
          
        </Card>
      </div>
      <div class="view" v-else-if="active === 'park'">
        <div class="tiles">
          <StatTile label="공영주차장" :value="fmt(parkData.length) + '곳'" icon="car" accent />
          <StatTile label="지도 표시" :value="fmt(parkPlot.length) + '곳'" icon="car" />
        </div>
        <Card title="주차장 지도 — 화성시">
          <div ref="parkEl" class="evmap"></div>
        </Card>
        <Card title="주차장 목록">
          <DataTable :cols="['주차장', '주소', '행정동']" :rows="parkRows" />
        </Card>
      </div>
      <div class="view" v-else>
        <div class="tiles">
          <StatTile label="수소차 충전소" :value="fmt(h2Data.length) + '곳'" icon="car" accent />
        </div>
        <Card title="수소차 충전소 지도 — 화성시">
          <div ref="h2El" class="evmap"></div>
        </Card>
        <Card title="충전소 목록">
          <DataTable :cols="['충전소', '주소', '행정동']" :rows="h2Rows" />
        </Card>
      </div>
  </MenuLayout>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 14px; }
.tiles { display: flex; gap: 14px; flex-wrap: wrap; }
.evmap { height: 520px; width: 100%; border-radius: 8px; overflow: hidden; }
.muted { color: #8fa3bd; padding: 1rem .5rem; font-size: .9rem; }
:deep(.leaflet-container) { background: #0c1b2e; font-family: inherit; }
@media (max-width: 720px) { .evmap { height: 360px; } }
</style>
