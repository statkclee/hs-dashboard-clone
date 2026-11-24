<script setup>
import { ref, onMounted, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import { loadJSON, loadGeo, loadCSV, fmt } from '../../lib/data.js'
import MenuLayout from '../MenuLayout.vue'
import Card from '../Card.vue'
import StatTile from '../StatTile.vue'
import DataTable from '../DataTable.vue'
import BarLineChart from '../BarLineChart.vue'
import LineChart from '../LineChart.vue'
import PopMap from '../PopMap.vue'

const items = [
  { label: '인구현황', key: 'pop' },
  { label: '공공시설 현황', key: 'fac' },
  { label: '교류도시', key: 'sister' },
  { label: '일자리 현황', key: 'job' },
]
const sub = ref('pop')

const pop = ref({})
const geo = ref(null)
const sister = ref([])
onMounted(async () => {
  try { pop.value = await loadJSON('population') } catch (e) { pop.value = {} }
  try { geo.value = await loadGeo('hwaseong_emd.geojson') } catch (e) { geo.value = null }
  try { sister.value = (await loadCSV('교류도시.csv')) || [] } catch (e) { sister.value = [] }
  try { fac.value = await loadGeo('공공시설.json') } catch (e) { fac.value = null }
  try { job.value = await loadGeo('일자리현황.json') } catch (e) { job.value = null }
})
const sisterCols = computed(() => (sister.value[0] ? Object.keys(sister.value[0]) : []))
const sisterRows = computed(() => sister.value.map((r) => sisterCols.value.map((c) => r[c])))
const sisterCount = computed(() => ({
  dom: sister.value.filter((r) => (r['범위'] || '').includes('국내')).length,
  intl: sister.value.filter((r) => (r['범위'] || '').includes('국외') || (r['범위'] || '').includes('해외')).length,
}))

const dongs = computed(() => (pop.value?.status === 'ok' ? pop.value.dongs : []))
const labels = computed(() => dongs.value.map((d) => d.dong))
const bars = computed(() => [{ label: '인구', data: dongs.value.map((d) => d.total), color: '#167aff' }])

const gender = [
  { k: '남', v: '518,920' },
  { k: '여', v: '483,217' },
  { k: '외국인', v: '71,865' },
]
const vital = [
  { k: '출생', v: '654', s: '남 319 · 여 335' },
  { k: '사망', v: '356', s: '남 183 · 여 173' },
]
const ages = [
  { k: '영유아 (0~5)', v: '49,322' },
  { k: '아동청소년 (0~17)', v: '184,354' },
  { k: '청소년 (9~24)', v: '173,604' },
  { k: '청년 (19~39)', v: '284,391' },
  { k: '중장년 (40~64)', v: '398,450' },
  { k: '어르신 (65+)', v: '123,637' },
]

const trendLabels = ['6월', '7월', '8월', '9월', '10월']
const trendSeries = [
  { label: '출생', data: [882, 788, 768, 693, 654], color: '#4da3ff' },
  { label: '사망', data: [372, 361, 355, 349, 356], color: '#ff7a7a' },
]

// ---- 공공시설 ----
const fac = ref(null)
const facEl = ref(null)
let map = null
let layers = []
const CAT_COLORS = ['#2c67df', '#2fa84f', '#f5a623', '#b05be6', '#e53935']
const activeCats = ref(new Set([0, 1, 2, 3, 4]))
const facCats = computed(() => fac.value?.cats || [])
const allOn = computed(() => facCats.value.length > 0 && activeCats.value.size === facCats.value.length)
function toggleCat(i) {
  const s = new Set(activeCats.value)
  if (s.has(i)) s.delete(i); else s.add(i)
  activeCats.value = s
  syncLayers()
}
function toggleAll() {
  activeCats.value = allOn.value ? new Set() : new Set(facCats.value.map((_, i) => i))
  syncLayers()
}
function syncLayers() {
  if (!map) return
  layers.forEach((g, i) => {
    if (!g) return
    const on = activeCats.value.has(i)
    if (on && !map.hasLayer(g)) g.addTo(map)
    else if (!on && map.hasLayer(g)) map.removeLayer(g)
  })
}
function destroyFacMap() { if (map) { map.remove(); map = null } layers = [] }
function renderFacMap() {
  destroyFacMap()
  if (!facEl.value || !fac.value) return
  map = L.map(facEl.value, { scrollWheelZoom: true }).setView([37.2, 126.9], 11)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '© OpenStreetMap' }).addTo(map)
  const cats = fac.value.cats
  layers = cats.map(() => L.layerGroup())
  const pts = []
  for (const it of fac.value.items || []) {
    if (it.lat == null || it.lng == null || layers[it.cat] == null) continue
    pts.push([it.lat, it.lng])
    L.circleMarker([it.lat, it.lng], { radius: 5, fillColor: CAT_COLORS[it.cat], color: '#fff', weight: 1, fillOpacity: 0.85 })
      .bindTooltip(`${it.nm} · ${cats[it.cat]}`).addTo(layers[it.cat])
  }
  syncLayers()
  if (pts.length) map.fitBounds(pts, { padding: [20, 20] })
}

// ---- 일자리 ----
const job = ref(null)
const jobKpi = computed(() => {
  const k = job.value?.kpi
  if (!k) return []
  return [
    { label: '고용률', value: k['고용률'] + '%', d: k['고용률증감'], unit: '%' },
    { label: '실업률', value: k['실업률'] + '%', d: k['실업률증감'], unit: '%' },
    { label: '취업자 수', value: fmt(k['취업자수']) + '명', d: k['취업자증감'], unit: '명' },
  ]
})
const fmtDelta = (d, unit) => (d > 0 ? '▲ +' : d < 0 ? '▼ ' : '') + (unit === '명' ? fmt(d) : d) + unit
const empLabels = computed(() => (job.value?.고용률추이 || []).map((p) => p[0]))
const empBars = computed(() => [{ label: '고용률', data: (job.value?.고용률추이 || []).map((p) => p[1]), color: '#167aff' }])
const unempLabels = computed(() => (job.value?.실업률추이 || []).map((p) => p[0]))
const unempBars = computed(() => [{ label: '실업률', data: (job.value?.실업률추이 || []).map((p) => p[1]), color: '#e0527a' }])
const pubRows = computed(() => {
  const g = job.value?.공공일자리
  if (!g) return []
  return [['목표', fmt(g.목표합계), ...g.목표.map(fmt)], ['실적', fmt(g.실적합계), ...g.실적.map(fmt)]]
})
const pubCols = computed(() => ['구분', '합계', ...(job.value?.공공일자리?.cols || [])])

watch(sub, async (k) => {
  if (k === 'fac') { await nextTick(); renderFacMap() } else destroyFacMap()
})
watch(fac, async () => { if (sub.value === 'fac') { await nextTick(); renderFacMap() } })
onBeforeUnmount(destroyFacMap)
</script>

<template>
  <MenuLayout icon="chart-line" title="도시현황" :items="items" v-model="sub">
    <div class="view" v-if="sub === 'pop'">
      <Card title="생활 인구 정보">
        <div class="tiles">
          <StatTile label="총인구" value="1,074,002명" icon="family" accent />
          <StatTile label="전국 순위" value="4위" icon="trophy" />
          <StatTile label="경기도 총인구" value="13,780,735명" icon="family" />
          <StatTile label="평균연령 (경기 44.0세)" value="40.0세" icon="users" />
        </div>
        <div class="grid g3">
          <div v-for="g in gender" :key="g.k" class="cell"><span class="k">{{ g.k }}</span><span class="v">{{ g.v }}</span></div>
        </div>
        <div class="grid g2">
          <div v-for="g in vital" :key="g.k" class="cell">
            <span class="k">{{ g.k }}</span><span class="v">{{ g.v }}</span><span class="s">{{ g.s }}</span>
          </div>
        </div>
        <div class="grid g3">
          <div v-for="g in ages" :key="g.k" class="cell"><span class="k">{{ g.k }}</span><span class="v">{{ g.v }}</span></div>
        </div>
        <div class="cap">기준: 2026년 10월 · 출처 행정안전부</div>
      </Card>

      <Card title="읍면동별 인구 세부사항">
        <BarLineChart :labels="labels" :bars="bars" :height="300" />
      </Card>

      <Card title="읍면동 인구 지도">
        <PopMap v-if="geo" :geo="geo" :pop="pop" />
        <div v-else class="cap">지도 불러오는 중…</div>
      </Card>

      <Card title="출생/사망 인구 추이">
        <LineChart :labels="trendLabels" :series="trendSeries" :height="260" />
        <div class="cap">표시값(월별 추이)</div>
      </Card>
    </div>

    <div class="view" v-else-if="sub === 'sister'">
      <div class="tiles">
        <StatTile label="교류도시" :value="sister.length + '곳'" icon="family" accent />
        <StatTile label="국내 자매·우호" :value="sisterCount.dom + '곳'" icon="pin" />
        <StatTile label="국외 자매·우호" :value="sisterCount.intl + '곳'" icon="family" />
      </div>
      <Card title="국내외 교류도시 — 자매·우호도시">
        <DataTable :cols="sisterCols" :rows="sisterRows" />
      </Card>
    </div>

    <div class="view" v-else-if="sub === 'fac'">
      <div class="tiles">
        <StatTile label="공공시설" :value="fmt(fac?.total) + '곳'" icon="pin" accent />
        <StatTile label="지도 표시" :value="fmt(fac?.mapped) + '곳'" icon="pin" />
      </div>
      <Card title="공공시설 지도">
        <div class="filters" v-if="fac">
          <button type="button" class="chip" :class="{ off: !allOn }" @click="toggleAll">전체</button>
          <button v-for="(c, i) in fac.cats" :key="i" type="button" class="chip" :class="{ off: !activeCats.has(i) }" @click="toggleCat(i)">
            <span class="sw" :style="{ background: CAT_COLORS[i] }"></span>{{ c }} {{ fmt(fac.counts[i]) }}
          </button>
        </div>
        <div ref="facEl" class="facmap" v-show="fac"></div>
        <div v-if="!fac" class="cap">지도 불러오는 중…</div>
        <div class="cap">범례 버튼을 눌러 분류별로 표시/숨김 · 좌표 없는 시설은 지도에서 제외</div>
      </Card>
    </div>

    <div class="view" v-else-if="sub === 'job'">
      <template v-if="job">
        <Card :title="'고용 지표 (' + job.기준 + ')'">
          <div class="tiles">
            <div v-for="t in jobKpi" :key="t.label" class="kpi">
              <span class="k">{{ t.label }}</span>
              <span class="kv">{{ t.value }}</span>
              <span class="kd" :class="t.d > 0 ? 'up' : t.d < 0 ? 'down' : ''">{{ fmtDelta(t.d, t.unit) }}</span>
            </div>
          </div>
        </Card>

        <Card title="고용률 추이">
          <BarLineChart :labels="empLabels" :bars="empBars" :height="260" />
        </Card>
        <Card title="실업률 추이">
          <BarLineChart :labels="unempLabels" :bars="unempBars" :height="260" />
        </Card>

        <Card title="취업자 수 현황">
          <div class="grid g2">
            <div>
              <div class="grp">성별</div>
              <div v-for="r in job.성별" :key="r[0]" class="pb">
                <div class="pbh"><span class="k">{{ r[0] }}</span><span class="v">{{ fmt(r[1]) }}명 · {{ r[2] }}%</span></div>
                <div class="track"><div class="bar" :style="{ width: r[2] + '%', background: '#167aff' }"></div></div>
              </div>
            </div>
            <div>
              <div class="grp">연령별</div>
              <div v-for="r in job.연령별" :key="r[0]" class="pb">
                <div class="pbh"><span class="k">{{ r[0] }}</span><span class="v">{{ fmt(r[1]) }}명 · {{ r[2] }}%</span></div>
                <div class="track"><div class="bar" :style="{ width: r[2] + '%', background: '#2fa84f' }"></div></div>
              </div>
            </div>
          </div>
        </Card>

        <Card title="공공일자리">
          <div class="tiles">
            <StatTile label="채용인원" :value="fmt(job.공공일자리.채용인원) + '명'" icon="users" accent />
          </div>
          <div class="gap"><DataTable :cols="pubCols" :rows="pubRows" /></div>
        </Card>

        <Card title="민간일자리">
          <div class="tiles">
            <StatTile label="채용인원" :value="fmt(job.민간일자리.채용인원) + '명'" icon="users" accent />
            <StatTile label="구인등록" :value="fmt(job.민간일자리.구인등록)" icon="users" />
            <StatTile label="구직등록" :value="fmt(job.민간일자리.구직등록)" icon="users" />
            <StatTile label="취업률" :value="job.민간일자리.취업률 + '%'" icon="trophy" />
          </div>
          <div class="cap">출처: {{ job.source }}</div>
        </Card>
      </template>
      <Card v-else title="일자리 현황"><div class="cap">불러오는 중…</div></Card>
    </div>

    <div class="view" v-else>
      <Card :title="items.find((i) => i.key === sub)?.label">
        <div class="cap">해당 데이터 연동 예정입니다.</div>
      </Card>
    </div>
  </MenuLayout>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 14px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
.grid { display: grid; gap: 10px; margin-top: 12px; }
.g3 { grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }
.g2 { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
.cell { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; padding: 10px 12px; border: 1px solid var(--rule); border-radius: 8px; }
.k { color: var(--muted); font-size: .85rem; }
.v { color: var(--ink); font-weight: 800; font-size: 1.05rem; margin-left: auto; }
.s { color: var(--muted); font-size: .78rem; width: 100%; text-align: right; }
.cap { color: var(--muted); font-size: .8rem; margin-top: 10px; }
.filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 5px 11px; border: 1px solid var(--rule); border-radius: 999px; background: transparent; color: var(--ink); font-size: .82rem; cursor: pointer; }
.chip.off { opacity: .4; }
.sw { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.facmap { height: 560px; width: 100%; border-radius: 8px; overflow: hidden; }
.facmap :deep(.leaflet-container), :deep(.leaflet-container) { background: #0c1b2e; }
@media (max-width: 720px) { .facmap { height: 380px; } }
.kpi { display: flex; flex-direction: column; gap: 4px; padding: 14px; border: 1px solid var(--rule); border-radius: 10px; }
.kv { color: var(--ink); font-weight: 800; font-size: 1.5rem; }
.kd { font-size: .85rem; color: var(--muted); }
.kd.up { color: #e53935; }
.kd.down { color: #2c67df; }
.grp { font-weight: 700; margin-bottom: 8px; color: var(--ink); }
.pb { margin-bottom: 10px; }
.pbh { display: flex; justify-content: space-between; gap: 8px; margin-bottom: 4px; }
.track { height: 10px; background: rgba(127,127,127,.18); border-radius: 5px; overflow: hidden; }
.bar { height: 100%; border-radius: 5px; }
.gap { margin-top: 12px; }
</style>
