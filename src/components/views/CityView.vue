<script setup>
import { ref, onMounted, computed } from 'vue'
import { loadJSON, loadGeo, loadCSV } from '../../lib/data.js'
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
</style>
