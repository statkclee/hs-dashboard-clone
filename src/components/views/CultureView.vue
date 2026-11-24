<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import L from 'leaflet'
import MenuLayout from '../MenuLayout.vue'
import Card from '../Card.vue'
import Calendar from '../Calendar.vue'
import EventsList from '../EventsList.vue'
import StatTile from '../StatTile.vue'
import DataTable from '../DataTable.vue'
import { loadCSV, loadGeo } from '../../lib/data.js'

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

const CATS = ['자연', '역사', '문화']
const COLORS = { 자연: '#2fa84f', 역사: '#c0712c', 문화: '#8a5cf0' }
const tour = ref({ counts: {}, total: 0, mapped: 0, items: [] })
const activeCats = ref(new Set(CATS))
const selected = ref(null)

const visibleItems = computed(() => tour.value.items.filter((t) => activeCats.value.has(t.cat)))
const tableRows = computed(() => visibleItems.value.map((t) => [t.nm, t.cat, t.addr, t.tel || '—']))

function toggleCat(c) {
  const s = new Set(activeCats.value)
  if (c === 'all') {
    activeCats.value = new Set(CATS)
    return
  }
  if (s.has(c)) s.delete(c)
  else s.add(c)
  activeCats.value = s
}

const mapEl = ref(null)
let map = null
let layer = null

function destroyMap() {
  if (map) {
    map.remove()
    map = null
    layer = null
  }
}

function drawMarkers(fit) {
  if (!map) return
  if (layer) layer.clearLayers()
  else layer = L.layerGroup().addTo(map)
  const pts = []
  visibleItems.value.forEach((t) => {
    if (t.lat == null || t.lng == null) return
    L.circleMarker([t.lat, t.lng], {
      radius: 7,
      color: '#fff',
      weight: 1.5,
      fillColor: COLORS[t.cat] || '#888',
      fillOpacity: 0.9,
    })
      .bindTooltip(t.nm)
      .on('click', () => {
        selected.value = t
      })
      .addTo(layer)
    pts.push([t.lat, t.lng])
  })
  if (fit && pts.length) map.fitBounds(pts, { padding: [30, 30] })
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
  if (!map.getZoom()) map.setView([37.2, 126.85], 10)
  drawMarkers(true)
  map.invalidateSize()
  setTimeout(() => map && map.invalidateSize(), 0)
}

watch(activeCats, () => drawMarkers(true))
watch(tour, () => drawMarkers(true))

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
  try {
    const d = await loadGeo('관광지.json')
    if (d) tour.value = d
  } catch (e) {}
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
      <div class="tiles">
        <StatTile label="관광지" :value="`${tour.total}곳`" icon="landmark" accent />
        <StatTile v-for="c in CATS" :key="c" :label="c" :value="`${tour.counts[c] ?? 0}곳`" icon="pin" />
      </div>
      <div class="cols">
        <Card title="관광지도 — 화성시">
          <div class="filters">
            <button type="button" class="fbtn" :class="{ on: activeCats.size === CATS.length }" @click="toggleCat('all')">전체</button>
            <button
              v-for="c in CATS"
              :key="c"
              type="button"
              class="fbtn"
              :class="{ on: activeCats.has(c) }"
              @click="toggleCat(c)"
            >
              <span class="sw" :style="{ background: COLORS[c] }"></span>{{ c }}
            </button>
          </div>
          <div ref="mapEl" class="tmap"></div>
        </Card>
        <div class="rightcol">
          <Card title="상세">
            <template v-if="selected">
              <dl class="detail">
                <dt>구분</dt>
                <dd><span class="sw" :style="{ background: COLORS[selected.cat] }"></span>{{ selected.cat }}</dd>
                <dt>관광지명</dt>
                <dd>{{ selected.nm }}</dd>
                <dt>주소</dt>
                <dd>{{ selected.addr || '—' }}</dd>
                <dt>문의전화</dt>
                <dd>{{ selected.tel || '—' }}</dd>
              </dl>
            </template>
            <div v-else class="hint">지도의 마커를 선택하면 상세 정보가 표시됩니다.</div>
          </Card>
          <Card title="관광지 목록">
            <div class="list-scroll">
              <DataTable :cols="['관광지명', '구분', '주소', '문의전화']" :rows="tableRows" />
            </div>
          </Card>
        </div>
      </div>
    </template>
  </MenuLayout>
</template>

<style scoped>
.tmap { height: 520px; width: 100%; min-width: 0; }
.tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 12px; }
.filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.fbtn { display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; border-radius: 16px; border: 1px solid #3a4a60; background: transparent; color: #aab; cursor: pointer; font: inherit; opacity: .6; }
.fbtn.on { opacity: 1; color: #fff; border-color: #6c86a8; background: rgba(255,255,255,.06); }
.sw { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
.fbtn .sw { margin-right: 0; }
.cols { display: grid; grid-template-columns: 1.55fr 1fr; gap: 14px; align-items: start; }
.rightcol { display: flex; flex-direction: column; gap: 14px; }
.list-scroll { max-height: 360px; overflow-y: auto; }
.detail { margin: 0; }
.detail dt { font-size: .8rem; color: #8fa3bd; margin-top: 8px; }
.detail dd { margin: 2px 0 0; color: #fff; word-break: keep-all; }
.hint { color: #8fa3bd; font-size: .85rem; }
.tmap :deep(.leaflet-container),
:deep(.leaflet-container) { background: #0c1b2e; font-family: inherit; }
.month-title { font-size: 1.3rem; font-weight: 800; text-align: center; margin-bottom: 12px; color: #fff; }
@media (max-width: 900px) { .cols { grid-template-columns: 1fr; } }
@media (max-width: 800px) { .tiles { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .tmap { height: 360px; } }
</style>
