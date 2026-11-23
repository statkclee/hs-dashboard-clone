<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue'
import L from 'leaflet'
import { loadJSON, fmt } from '../../lib/data.js'
import Card from '../Card.vue'
import DataTable from '../DataTable.vue'
import StatTile from '../StatTile.vue'

const ev = ref({})
const mapEl = ref(null)
let map = null

onMounted(async () => {
  ev.value = await loadJSON('evcharger')
  await nextTick()
  renderMap()
})
onBeforeUnmount(() => { if (map) { map.remove(); map = null } })

function renderMap() {
  if (!mapEl.value || ev.value?.status !== 'ok') return
  map = L.map(mapEl.value, { scrollWheelZoom: true }).setView([37.2, 126.9], 11)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '© OpenStreetMap' }).addTo(map)
  const pts = []
  ev.value.chargers.forEach((c) => {
    const lat = parseFloat(c.lat), lng = parseFloat(c.lng)
    if (!lat || !lng) return
    pts.push([lat, lng])
    L.circleMarker([lat, lng], { radius: 3, color: '#167aff', weight: 1, fillColor: '#2c67df', fillOpacity: 0.7 })
      .bindTooltip(c.name || '충전소').addTo(map)
  })
  if (pts.length) map.fitBounds(pts, { padding: [20, 20] })
}

const ok = computed(() => ev.value?.status === 'ok')
const rows = computed(() => (ok.value ? ev.value.chargers.slice(0, 40).map((c) => [c.name, c.addr, c.connectors]) : []))
</script>

<template>
  <div class="view">
    <div class="tiles">
      <StatTile label="전기차 충전소" :value="ok ? fmt(ev.n) + '곳' : '— (수집 대기)'" icon="car" accent />
    </div>
    <div class="cols">
      <Card title="전기차 충전소 지도 — 화성시 (Leaflet · 공개 타일)">
        <div ref="mapEl" class="evmap"></div>
      </Card>
      <Card title="충전소 목록">
        <p v-if="ok" class="muted small">화성시 충전소 {{ fmt(ev.n) }}곳 (상위 40 표시)</p>
        <DataTable :cols="['충전소', '주소', '충전기수']" :rows="rows" />
      </Card>
    </div>
  </div>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 14px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
.cols { display: grid; grid-template-columns: 1.4fr 1fr; gap: 14px; align-items: start; }
@media (max-width: 1000px) { .cols { grid-template-columns: 1fr; } }
.evmap { height: 560px; width: 100%; }
.cols :deep(.card-b):has(.evmap) { padding: 0; }
:deep(.leaflet-container) { background: #0c1b2e; font-family: inherit; }
</style>
