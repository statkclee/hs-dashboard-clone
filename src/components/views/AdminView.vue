<script setup>
import { ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import MenuLayout from '../MenuLayout.vue'
import Card from '../Card.vue'
import Icon from '../Icon.vue'
import DataTable from '../DataTable.vue'
import StatTile from '../StatTile.vue'
import DonutChart from '../DonutChart.vue'
import { loadCSV, loadJSON, loadGeo, fmt } from '../../lib/data.js'

const active = ref('stature')
const items = [
  { label: '화성특례시의 위상', key: 'stature' },
  { label: '시정현황', key: 'admin' },
  { label: '시정홍보', key: 'pr' },
  { label: '주민참여예산', key: 'budget' },
]

const idx = ref([])
const card = ref([])

// 관측된 공개 표시값(CSV에 없을 때의 폴백)
const FALLBACK = [
  { name: '평균연령', value: '화성시 40.2세', rank: '전국 기초 1위', note: '가장 젊은 도시' },
  { name: '인구수', value: '108만명 (1,073,059명)', rank: '전국 4위' },
  { name: '아동인구수', value: '184,796명', rank: '전국 1위' },
  { name: 'GRDP(지역내총생산)', value: '90조 3,678억원', rank: '전국 1위' },
  { name: '월간 수출규모', value: '172억 3,329만 달러', rank: '경기도 4위' },
  { name: '사업체 수', value: '126,252개', rank: '경기도 1위' },
  { name: '종사자 수', value: '618,410명', rank: '경기도 1위' },
  { name: '제조업체 수', value: '25,624개', rank: '전국 1위' },
]
const SKIP = ['지방자치경쟁력지수', '재정자립도', '개발가능면적']
const norm = (s) => String(s || '').replace(/\(.*?\)/g, '').replace(/\s+/g, '')

const awards = ref([])

// 주민참여예산
const budget = ref(null)
const geo = ref(null)
const mapEl = ref(null)
let map = null
let layer = null
const STOPS = ['#e8f0ff', '#a9c7ff', '#5f9bff', '#2f6fe0', '#1b4fae']
const colorOf = (n) => (n <= 0 ? STOPS[0] : STOPS[Math.min(STOPS.length - 1, Math.ceil(n * (STOPS.length - 1) / 6))])
const bSum = computed(() => budget.value?.summary || {})
const regionCount = computed(() => Object.fromEntries(budget.value?.region || []))
const budgetCols = ['지역', '사업명', '담당부서', '예산액(천원)', '집행액(천원)', '상태']
const budgetRows = computed(() =>
  (budget.value?.items || []).map((r) => [r.reg, r.nm, r.dept, fmt(r.bud), fmt(r.exe), r.done]))

function destroyMap() {
  if (map) { map.remove(); map = null; layer = null }
}
function renderMap() {
  if (!mapEl.value || !geo.value || !budget.value) return
  destroyMap()
  map = L.map(mapEl.value, { zoomControl: true, scrollWheelZoom: true }).setView([37.17, 126.92], 10)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18, attribution: '© OpenStreetMap',
  }).addTo(map)
  layer = L.geoJSON(geo.value, {
    style: (f) => ({
      fillColor: colorOf(regionCount.value[f.properties.dong] || 0),
      fillOpacity: 0.78, color: '#ffffff', weight: 1,
    }),
    onEachFeature: (f, l) => {
      const n = regionCount.value[f.properties.dong] || 0
      l.bindTooltip(`${f.properties.dong} · ${n}건`, { sticky: true })
    },
  }).addTo(map)
  map.fitBounds(layer.getBounds(), { padding: [12, 12] })
}
watch(active, async (v) => {
  if (v === 'budget') { await nextTick(); renderMap() } else destroyMap()
})
watch([budget, geo], async () => {
  if (active.value === 'budget') { await nextTick(); renderMap() }
})
onBeforeUnmount(destroyMap)
onMounted(async () => {
  const [a, b, c, bj, g] = await Promise.all([
    loadCSV('위상지표.csv'), loadCSV('위상카드-다모아.csv'), loadCSV('수상실적.csv'),
    loadGeo('주민참여예산.json'), loadGeo('hwaseong_emd.geojson'),
  ])
  budget.value = bj
  geo.value = g
  idx.value = a
  card.value = b
  awards.value = c || []
})
const awardCols = computed(() => (awards.value[0] ? Object.keys(awards.value[0]) : []))
const awardRows = computed(() => awards.value.map((r) => awardCols.value.map((c) => r[c])))

const metrics = computed(() => {
  const out = []
  const seen = new Set()
  const push = (m) => {
    const k = norm(m.name)
    if (seen.has(k)) return
    seen.add(k)
    out.push(m)
  }
  for (const r of card.value) {
    const range = (r['순위범위'] || '').replace('(기초)', ' 기초')
    push({ name: r['지표'], value: r['값표기'], rank: `${range} ${r['순위']}위`, note: r['비고'] })
  }
  for (const r of idx.value) {
    if (SKIP.includes(norm(r['지표']))) continue
    const n = Number(r['값'])
    const v = Number.isFinite(n) ? n.toLocaleString('ko-KR') : r['값']
    push({ name: r['지표'], value: `${v}${r['단위'] || ''}`, rank: r['순위'], note: '' })
  }
  for (const f of FALLBACK) push(f)
  return out
})

const GROUPS = [
  { key: 'pop', title: '인구현황', icon: 'users', color: '#2c67df', kw: ['인구', '평균연령', '아동', '출생'] },
  { key: 'eco', title: '지역경제 현황', icon: 'chart-column', color: '#e0a000', kw: ['GRDP', '수출', '총생산'] },
  { key: 'biz', title: '기업체', icon: 'building', color: '#2f8f5b', kw: ['사업체', '종사자', '제조업', '고용'] },
]
const groups = computed(() =>
  GROUPS.map((g) => ({
    ...g,
    rows: metrics.value.filter((m) => g.kw.some((k) => m.name.includes(k))
      && !GROUPS.slice(0, GROUPS.indexOf(g)).some((p) => p.kw.some((k) => m.name.includes(k)))),
  })),
)
</script>

<template>
  <MenuLayout icon="chart-column" title="행정현황" :items="items" v-model="active">
    <template v-if="active === 'stature'">
      <div class="banner">
        <div class="b-ic"><Icon name="trophy" :size="64" /></div>
        <div class="b-txt">
          <div class="b-title">화성특례시의 위상</div>
          <div class="b-sub">2025년 지방자치경쟁력지수(KCLI) 종합경쟁력 9년 연속 전국 <b>1위</b></div>
        </div>
      </div>

      <div class="grid3">
        <section v-for="g in groups" :key="g.key" class="gcard">
          <header class="gh" :style="{ background: g.color }">
            <Icon :name="g.icon" :size="18" /><span>{{ g.title }}</span>
          </header>
          <div class="gb">
            <div v-for="m in g.rows" :key="m.name" class="row">
              <div class="r-name">{{ m.name }}</div>
              <div class="r-val">{{ m.value }}</div>
              <div class="r-foot">
                <span v-if="m.rank" class="pill">{{ m.rank }}</span>
                <span v-if="m.note" class="note">{{ m.note }}</span>
              </div>
            </div>
            <div v-if="!g.rows.length" class="empty">데이터 없음</div>
          </div>
        </section>
      </div>
    </template>

    <template v-else-if="active === 'admin'">
      <div class="tiles">
        <StatTile label="최근 수상·평가 실적" :value="awards.length + '건'" icon="trophy" accent />
      </div>
      <Card title="시정현황 — 수상·평가 실적">
        <DataTable :cols="awardCols" :rows="awardRows" />
      </Card>
    </template>

    <template v-else-if="active === 'budget'">
      <div class="tiles">
        <StatTile label="완료 사업" :value="fmt(bSum['완료사업']) + '개'" icon="trophy" accent />
        <StatTile label="총 사업 개수" :value="fmt(bSum['총사업개수']) + '개'" icon="chart-column" />
        <StatTile label="집행액" :value="fmt(bSum['집행액']) + '천원'" icon="chart-column" />
        <StatTile label="예산액" :value="fmt(bSum['예산액']) + '천원'" icon="chart-column" />
      </div>
      <div class="donuts">
        <Card :title="`${budget?.year ?? ''}년도 사업 완료율`">
          <div class="donut"><DonutChart :percent="bSum['사업완료율'] || 0" color="#2c67df" :size="160" label="완료율" /></div>
        </Card>
        <Card :title="`${budget?.year ?? ''}년도 예산 집행률`">
          <div class="donut"><DonutChart :percent="bSum['예산집행률'] || 0" color="#2f8f5b" :size="160" label="집행률" /></div>
        </Card>
      </div>
      <Card title="읍면동별 사업 수">
        <div ref="mapEl" class="bmap"></div>
      </Card>
      <Card title="사업 목록">
        <DataTable :cols="budgetCols" :rows="budgetRows" />
      </Card>
    </template>

    <Card v-else :title="items.find((i) => i.key === active)?.label">
      <div class="soon">해당 데이터 연동 예정입니다.</div>
    </Card>
  </MenuLayout>
</template>

<style scoped>
.banner {
  display: flex; align-items: center; gap: 20px;
  min-height: 120px; padding: 20px 28px; margin-bottom: 16px;
  border-radius: 10px; color: #fff;
  background: linear-gradient(90deg, #2a2a3e, #1b3a5c);
  border: 1px solid var(--rule);
}
.b-ic { color: #ffd166; display: flex; }
.b-title { font-size: 32px; font-weight: 800; letter-spacing: -0.5px; }
.b-sub { margin-top: 6px; font-size: 15px; color: #d6dbe6; }
.b-sub b { color: #ffd166; font-size: 1.15em; }
.grid3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
@media (max-width: 900px) { .grid3 { grid-template-columns: 1fr; } .b-title { font-size: 24px; } }
.gcard { border: 1px solid var(--rule); border-radius: 10px; overflow: hidden; }
.gh { display: flex; align-items: center; gap: 8px; padding: 10px 14px; color: #fff; font-weight: 700; }
.gb { padding: 4px 14px 10px; }
.row { padding: 12px 0; border-bottom: 1px solid var(--rule); }
.row:last-child { border-bottom: 0; }
.r-name { font-size: 12px; color: var(--muted); }
.r-val { font-size: 22px; font-weight: 800; color: var(--ink); margin: 2px 0 6px; line-height: 1.25; }
.r-foot { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.pill { background: var(--blue2, #2c67df); color: #fff; font-size: 12px; font-weight: 600; padding: 2px 10px; border-radius: 999px; }
.note { font-size: 12px; color: var(--muted); }
.empty, .soon { color: var(--muted); padding: 24px 0; text-align: center; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 14px; }
.donuts { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; margin-bottom: 14px; }
.donut { display: flex; justify-content: center; padding: 8px 0; }
.bmap { height: 520px; width: 100%; }
:deep(.leaflet-container) { background: #0c1b2e; font-family: inherit; }
</style>
