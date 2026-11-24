<script setup>
import { ref, onMounted, computed } from 'vue'
import { loadCSV, num } from '../../lib/data.js'
import MenuLayout from '../MenuLayout.vue'
import Card from '../Card.vue'
import DataTable from '../DataTable.vue'
import StatTile from '../StatTile.vue'
import DonutChart from '../DonutChart.vue'

const base = import.meta.env.BASE_URL || './'
const sub = ref('pledge')
const items = [
  { label: '공약사업', key: 'pledge' },
  { label: '중장기발전계획', key: 'plan' },
]

const cat = ref([])
onMounted(async () => {
  cat.value = await loadCSV('공약사업-분야별.csv')
})

const stages = [
  { label: '미추진', pct: 0, n: 0, color: '#bcd7ff' },
  { label: '일부추진', pct: 2, n: 2, color: '#8dbcff' },
  { label: '정상추진', pct: 23, n: 20, color: '#5a9dff' },
  { label: '계속추진', pct: 43, n: 38, color: '#2f84ff' },
  { label: '완료', pct: 32, n: 28, color: '#0b5fd6' },
]

const fields = [
  { name: '균형발전 특례시', pct: 80.5, color: '#e45b5b', keys: ['균형발전'] },
  { name: '스마트 미래도시', pct: 100.0, color: '#2bc4c4', keys: ['스마트'] },
  { name: '포용적 복지도시', pct: 96.6, color: '#8b7ff0', keys: ['포용'] },
  { name: '친환경 생태문화도시', pct: 82.2, color: '#9fcf3a', keys: ['친환경', '생태'] },
  { name: '지역상생 기업도시', pct: 90.7, color: '#f0a93a', keys: ['지역상생', '기업'] },
]

const fieldCards = computed(() =>
  fields.map((f, i) => {
    const row = cat.value.find((r) => f.keys.some((k) => (r['분야'] || '').includes(k)))
    const done = row ? num(row['완료']) : null
    return { ...f, no: i + 1, done }
  })
)

const catCols = computed(() => (cat.value[0] ? Object.keys(cat.value[0]) : []))
const catRows = computed(() => cat.value.map((r) => catCols.value.map((c) => r[c])))
</script>

<template>
  <MenuLayout icon="clipboard" title="사업관리" :items="items" v-model="sub">
    <template v-if="sub === 'pledge'">
      <Card title="전체 추진 현황">
        <div class="top">
          <div class="top-l">
            <StatTile label="이행 완료 공약" value="66 / 88 건" icon="clipboard" />
            <div class="rate">75.00%</div>
          </div>
          <div class="top-m">
            <DonutChart :percent="91.5" color="#167aff" label="추진율" :size="190" />
          </div>
          <div class="top-r">
            <div v-for="s in stages" :key="s.label" class="srow">
              <span class="slabel">{{ s.label }}</span>
              <div class="track"><div class="bar" :style="{ width: s.pct + '%', background: s.color }"></div></div>
              <span class="sval">{{ s.pct }}% ({{ s.n }}건)</span>
            </div>
          </div>
        </div>
      </Card>

      <div class="fields">
        <div v-for="f in fieldCards" :key="f.name" class="field">
          <div class="fhead" :style="{ background: f.color }">
            <span class="fno">{{ f.no }}</span><span class="fname">{{ f.name }}</span>
          </div>
          <div class="fbody">
            <DonutChart :percent="f.pct" :color="f.color" :size="130" />
            <div class="fdone">완료 <b>{{ f.done ?? '—' }}</b>건</div>
          </div>
        </div>
      </div>

      <Card title="사업목록">
        <DataTable :cols="catCols" :rows="catRows" />
      </Card>
    </template>

    <Card v-else title="중장기발전계획 — 화성시 발전구상도">
      <div class="planmap">
        <img :src="`${base}assets/중장기발전계획.png`" alt="화성시 중장기발전계획 구상도" />
      </div>
      <p class="cap">마리나항·국제테마파크·GTX-A·고속도로·철도 등 주요 발전사업. 출처: 다모아 공개 표시값</p>
    </Card>
  </MenuLayout>
</template>

<style scoped>
.top { display: grid; grid-template-columns: 1fr auto 1.4fr; gap: 24px; align-items: center; }
.top-l { display: flex; flex-direction: column; gap: 10px; }
.rate { color: #ff9a2e; font-weight: 800; font-size: 1.8rem; text-align: center; }
.top-m { display: flex; justify-content: center; }
.top-r { display: flex; flex-direction: column; gap: 10px; }
.srow { display: grid; grid-template-columns: 4.5em 1fr 6.5em; gap: 10px; align-items: center; font-size: .9rem; }
.slabel { color: var(--muted); }
.track { height: 14px; background: rgba(255,255,255,.07); border-radius: 7px; overflow: hidden; }
.bar { height: 100%; border-radius: 7px; min-width: 2px; }
.sval { color: #fff; text-align: right; font-variant-numeric: tabular-nums; }
.fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; margin: 16px 0; }
.field { border: 1px solid var(--rule); border-radius: 10px; overflow: hidden; background: rgba(255,255,255,.02); }
.fhead { display: flex; align-items: center; gap: 8px; padding: 9px 12px; color: #fff; font-weight: 700; font-size: .92rem; }
.fno { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 50%; background: rgba(0,0,0,.28); font-size: .8rem; flex: none; }
.fbody { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 16px 8px; }
.fdone { color: var(--muted); font-size: .9rem; }
.fdone b { color: #fff; font-size: 1.1rem; }
.muted { color: var(--muted); padding: 24px 0; text-align: center; }
.planmap { width: 100%; overflow: hidden; border-radius: 8px; background: #0c1b2e; }
.planmap img { width: 100%; height: auto; display: block; }
.cap { color: var(--muted); font-size: .8rem; margin-top: 8px; }
@media (max-width: 900px) {
  .top { grid-template-columns: 1fr; }
}
</style>
