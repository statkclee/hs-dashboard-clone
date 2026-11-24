<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import L from 'leaflet'
import { loadJSON, fmt } from '../../lib/data.js'
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
const parking = ref(null)
const mapEl = ref(null)
let map = null

const chargers = computed(() => (ev.value?.status === 'ok' && Array.isArray(ev.value.chargers) ? ev.value.chargers : []))
const total = computed(() => ev.value?.n ?? chargers.value.length)
const evRows = computed(() => chargers.value.slice(0, 40).map((c) => [c.name, c.addr, c.connectors]))
const parkItems = computed(() => (parking.value?.status === 'ok' && Array.isArray(parking.value.items) ? parking.value.items : []))
const parkCols = computed(() => (parkItems.value[0] ? Object.keys(parkItems.value[0]) : []))
const parkRows = computed(() => parkItems.value.map((r) => parkCols.value.map((c) => r[c])))

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

onMounted(async () => {
  ev.value = await loadJSON('evcharger')
  parking.value = await loadJSON('parking')
  await nextTick()
  if (active.value === 'ev') renderMap()
})
watch(active, async (k) => {
  if (k === 'ev') { await nextTick(); renderMap() } else destroyMap()
})
onBeforeUnmount(destroyMap)
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
        <Card title="주차장">
          
            <DataTable v-if="parkItems.length" :cols="parkCols" :rows="parkRows" />
            <div v-else class="muted">서버 수집 대기(승인된 API 활성화 후)</div>
          
        </Card>
      </div>
      <div class="view" v-else>
        <Card title="수소차 충전소">
          <div class="muted">준비 중</div>
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
