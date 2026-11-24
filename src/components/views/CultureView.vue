<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import L from 'leaflet'
import MenuLayout from '../MenuLayout.vue'
import Card from '../Card.vue'
import Calendar from '../Calendar.vue'
import EventsList from '../EventsList.vue'
import { loadCSV } from '../../lib/data.js'

const items = [
  { label: '행사정보', key: 'events' },
  { label: '관광지도', key: 'map' },
]
const active = ref('events')
const rows = ref([])

const YEAR = 2026
const MONTH = 11
const prefix = `${YEAR}-${String(MONTH).padStart(2, '0')}`

const monthRows = computed(() => rows.value.filter((r) => String(r['날짜'] || '').startsWith(prefix)))
const events = computed(() =>
  monthRows.value.map((r) => ({ day: Number(String(r['날짜']).slice(8, 10)), title: r['행사명'] }))
)

const spots = [
  ['제부도', 37.146, 126.603],
  ['궁평항', 37.126, 126.683],
  ['융건릉', 37.207, 126.979],
  ['용주사', 37.209, 126.983],
  ['전곡항', 37.19, 126.65],
  ['화성호', 37.07, 126.72],
]

const mapEl = ref(null)
let map = null

function destroyMap() {
  if (map) {
    map.remove()
    map = null
  }
}

async function buildMap() {
  await nextTick()
  if (active.value !== 'map' || !mapEl.value) return
  destroyMap()
  map = L.map(mapEl.value, { scrollWheelZoom: true })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)
  const pts = []
  spots.forEach(([name, lat, lng]) => {
    L.circleMarker([lat, lng], {
      radius: 7,
      color: '#ec6708',
      weight: 2,
      fillColor: '#ff7818',
      fillOpacity: 0.85,
    })
      .bindTooltip(name)
      .addTo(map)
    pts.push([lat, lng])
  })
  map.fitBounds(pts, { padding: [30, 30] })
  map.invalidateSize()
}

watch(active, (v) => {
  if (v === 'map') buildMap()
  else destroyMap()
})

onMounted(async () => {
  try {
    rows.value = (await loadCSV('행사.csv')) || []
  } catch (e) {
    rows.value = []
  }
  if (active.value === 'map') buildMap()
})

onBeforeUnmount(destroyMap)
</script>

<template>
  <MenuLayout icon="landmark" title="문화/관광" :items="items" v-model="active">
    <template v-if="active === 'events'">
      <Card title="행사 정보">
        <div class="month-title">{{ YEAR }}년 {{ MONTH }}월</div>
        <Calendar :year="YEAR" :month="MONTH" :events="events" />
      </Card>
      <Card title="이 달의 행사">
        <EventsList :rows="monthRows" />
      </Card>
    </template>
    <template v-else-if="active === 'map'">
      <Card title="관광지도 — 화성시">
        <div ref="mapEl" class="tmap"></div>
      </Card>
    </template>
  </MenuLayout>
</template>

<style scoped>
.tmap { height: 480px; width: 100%; }
.tmap :deep(.leaflet-container),
:deep(.leaflet-container) { background: #0c1b2e; font-family: inherit; }
.month-title { font-size: 1.3rem; font-weight: 800; text-align: center; margin-bottom: 12px; color: #fff; }
@media (max-width: 640px) { .tmap { height: 360px; } }
</style>
