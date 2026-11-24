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
const steep = ref({})
const steepFull = ref({}) // 다모아 전수 좌표(109곳)
const mapEl = ref(null)
const slopeMapEl = ref(null)
let map = null
let slopeMap = null
const sfOk = computed(() => steepFull.value?.status === 'ok')

const airOk = computed(() => air.value?.status === 'ok')
const lsOk = computed(() => landslide.value?.status === 'ok')
const ssOk = computed(() => steep.value?.status === 'ok')
const ssRows = computed(() =>
  ssOk.value ? (steep.value.items || []).map((r) => [r['지구명'], r['등급'], r['평가점수'], r['지정일'], r['지정사유']]) : [])
const ssGrades = computed(() => {
  const g = { D: 0, C: 0 }
  if (ssOk.value) for (const r of steep.value.items) { if (r['등급'] === 'D') g.D++; else if (r['등급'] === 'C') g.C++ }
  return g
})
const airRows = computed(() =>
  airOk.value ? (air.value.stations || []).map((s) => [s.station, fmt(s.pm10), fmt(s.pm25), s.o3 ?? '—']) : [])
const lsRows = computed(() =>
  lsOk.value ? (landslide.value.items || []).map((r) => [r['읍면동법정코드'], r['지명'], r['예상피해'] ?? '—']) : [])

function destroyMap() {
  if (map) { map.remove(); map = null }
}
function destroySlopeMap() {
  if (slopeMap) { slopeMap.remove(); slopeMap = null }
}
async function buildSlopeMap() {
  destroySlopeMap()
  await nextTick()
  if (!slopeMapEl.value || !sfOk.value) return
  slopeMap = L.map(slopeMapEl.value, { center: [37.17, 126.92], zoom: 11, scrollWheelZoom: false })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '&copy; OpenStreetMap' }).addTo(slopeMap)
  if (geo.value) {
    L.geoJSON(geo.value, { style: { fillColor: '#2c3e50', fillOpacity: 0.12, color: '#ffffff', weight: 1 } }).addTo(slopeMap)
  }
  // 재해위험도 등급색(원본은 균일 마커 — 클론은 지정 붕괴위험지역을 등급별로 차별화)
  const GCOL = { E: '#b71c1c', D: '#e53935', C: '#f5a623', B: '#f5d84a', A: '#2fa84f' }
  const norm = (s) => String(s || '').replace(/\(.*?\)/g, '').replace(/\s+/g, '')
  const desig = {} // 정규화 지구명 → 최고위험 등급
  if (ssOk.value) {
    const rank = { E: 5, D: 4, C: 3, B: 2, A: 1 }
    for (const r of steep.value.items || []) {
      const k = norm(r['지구명']); const g = r['등급']
      if (!desig[k] || (rank[g] || 0) > (rank[desig[k]] || 0)) desig[k] = g
    }
  }
  const matchGrade = (nm) => {
    const n = norm(nm)
    for (const k in desig) { if (n.includes(k) || k.includes(n)) return desig[k] }
    return null
  }
  const pts = []
  for (const s of steepFull.value.items || []) {
    if (!s.lat || !s.lng) continue
    pts.push([s.lat, s.lng])
    const g = matchGrade(s.nm)
    const color = g ? GCOL[g] : '#7a8aa0'
    const r = g ? 8 : 4.5
    L.circleMarker([s.lat, s.lng], {
      radius: r, color: '#fff', weight: g ? 2 : 1, fillColor: color, fillOpacity: g ? 0.95 : 0.7,
    }).bindTooltip(g ? `${s.nm} · ${s.dong} · 붕괴위험 ${g}등급` : `${s.nm} · ${s.dong} · 관리대상`).addTo(slopeMap)
  }
  if (pts.length) { try { slopeMap.fitBounds(pts, { padding: [20, 20] }) } catch (e) { /* ignore */ } }
  // 등급 범례
  const lg = L.control({ position: 'bottomright' })
  lg.onAdd = () => {
    const d = L.DomUtil.create('div', 'aq-legend')
    d.innerHTML = '<b>붕괴위험 등급</b>' +
      '<span><i style="background:#e53935"></i>D(위험)</span>' +
      '<span><i style="background:#f5a623"></i>C</span>' +
      '<span><i style="background:#2fa84f"></i>A</span>' +
      '<span><i style="background:#7a8aa0"></i>관리대상(미지정)</span>'
    return d
  }
  lg.addTo(slopeMap)
  setTimeout(() => slopeMap && slopeMap.invalidateSize(), 0)
}

async function buildMap() {
  destroyMap()
  await nextTick()
  if (!mapEl.value || !airOk.value) return
  map = L.map(mapEl.value, { center: [37.17, 126.92], zoom: 10, scrollWheelZoom: false })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18, attribution: '&copy; OpenStreetMap',
  }).addTo(map)
  // 읍면동 → 대기등급(색) 매핑 — 측정소명과 읍면동명 매칭(동탄 측정소는 동탄N동 전부)
  const byDong = {}
  for (const s of air.value.stations || []) {
    const [, color] = airGrade('pm10', s.pm10)
    byDong[s.station] = { color, pm10: s.pm10, grade: airGrade('pm10', s.pm10)[0] }
  }
  const matchDong = (dong) => {
    for (const st in byDong) {
      if (dong.includes(st) || st.includes(dong)) return byDong[st]
      if (st.startsWith('동탄') && dong.startsWith('동탄')) return byDong[st]
      if (st.startsWith('송산') && dong.startsWith('송산')) return byDong[st]
    }
    return null
  }
  if (geo.value) {
    const layer = L.geoJSON(geo.value, {
      style: (f) => {
        const m = matchDong(f.properties.dong)
        return { fillColor: m ? m.color : '#33465c', fillOpacity: m ? 0.72 : 0.35, color: '#ffffff', weight: 1 }
      },
      onEachFeature: (f, lyr) => {
        const m = matchDong(f.properties.dong)
        lyr.bindTooltip(m ? `${f.properties.dong} · PM10 ${m.pm10} (${m.grade})` : `${f.properties.dong} · 측정소 없음`,
          { sticky: true })
      },
    }).addTo(map)
    try { map.fitBounds(layer.getBounds()) } catch (e) { /* ignore */ }
  }
  // 범례(대시보드식)
  const legend = L.control({ position: 'bottomright' })
  legend.onAdd = () => {
    const div = L.DomUtil.create('div', 'aq-legend')
    div.innerHTML =
      '<b>미세먼지(PM10)</b>' +
      '<span><i style="background:#1c75d6"></i>좋음</span>' +
      '<span><i style="background:#2fa84f"></i>보통</span>' +
      '<span><i style="background:#f5a623"></i>나쁨</span>' +
      '<span><i style="background:#e53935"></i>매우나쁨</span>'
    return div
  }
  legend.addTo(map)
  setTimeout(() => map && map.invalidateSize(), 0)
}

onMounted(async () => {
  const [a, l, st, g, ss, sf] = await Promise.all([
    loadJSON('air'), loadJSON('landslide'), loadJSON('stations'), loadGeo('hwaseong_emd.geojson'),
    loadJSON('steepslope'), loadGeo('급경사지-전수.json'),
  ])
  air.value = a; landslide.value = l; stations.value = st; geo.value = g; steep.value = ss; steepFull.value = sf
  if (active.value === 'air') await buildMap()
  else if (active.value === 'slope') await buildSlopeMap()
})

watch(active, async (k) => {
  destroyMap(); destroySlopeMap()
  if (k === 'air') await buildMap()
  else if (k === 'slope') await buildSlopeMap()
})

onBeforeUnmount(() => { destroyMap(); destroySlopeMap() })
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

      <!-- 급경사지 -->
      <template v-else-if="active === 'slope'">
        <div class="tiles">
          <StatTile label="급경사지 관리대상(전수)" :value="sfOk ? steepFull.n + '곳' : '—'" icon="shield" accent />
          <StatTile label="붕괴위험지역 지정" :value="ssOk ? steep.n + '곳' : '—'" icon="shield" />
          <StatTile label="지정 D등급(위험)" :value="ssOk ? ssGrades.D + '곳' : '—'" icon="shield" />
        </div>
        <Card title="급경사지 지도 — 화성시 (관리대상 전수)">
          <div v-if="sfOk" ref="slopeMapEl" class="lmap"></div>
          <p v-else class="muted">수집 대기</p>
          <p class="cap">{{ steepFull.n }}곳 · 출처: 급경사지 전수(다모아 공개 표시값)</p>
        </Card>
        <Card title="붕괴위험지역 지정 현황 — 화성시 (safetydata)">
          <p v-if="!ssOk" class="muted">수집 대기</p>
          <template v-else>
            <p class="cap">전수 {{ sfOk ? steepFull.n : '—' }}곳 중 공식 '붕괴위험지역' 지정 {{ steep.n }}곳 · 재해위험도 등급(A~E)</p>
            <DataTable :cols="['지구명', '등급', '평가점수', '지정일', '지정사유']" :rows="ssRows" />
          </template>
        </Card>
      </template>

      <!-- 교통상황 / 자전거 -->
      <template v-else>
        <Card :title="items.find((i) => i.key === active)?.label">
          <p class="muted">해당 데이터 연동 예정입니다.</p>
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
.cap { color: var(--muted); font-size: .82rem; margin: 0 0 8px; }
:deep(.leaflet-container) { background: #0c1b2e; font-family: inherit; }
:deep(.aq-legend) { background: rgba(14,34,56,.92); color: #e8eef5; padding: 8px 10px; border-radius: 6px;
  font-size: 11px; line-height: 1.6; border: 1px solid rgba(255,255,255,.15); }
:deep(.aq-legend b) { display: block; margin-bottom: 4px; }
:deep(.aq-legend span) { display: inline-flex; align-items: center; margin-right: 8px; }
:deep(.aq-legend i) { width: 11px; height: 11px; border-radius: 2px; display: inline-block; margin-right: 4px; }
@media (max-width: 700px) { .lmap { height: 340px; } }
</style>
