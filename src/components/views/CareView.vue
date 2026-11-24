<script setup>
import { ref, onMounted } from 'vue'
import { loadCSV, fmt, num } from '../../lib/data.js'
import MenuLayout from '../MenuLayout.vue'
import Card from '../Card.vue'
import StatTile from '../StatTile.vue'
import BarLineChart from '../BarLineChart.vue'
import Icon from '../Icon.vue'

const items = [
  { label: '대상자 현황', key: 'target' },
  { label: '통합돌봄사업', key: 'biz' },
  { label: '서비스 제공 기관', key: 'org' },
  { label: '복지맵', key: 'map' },
  { label: '복지 대상자 현황', key: 'welfare' },
]
const active = ref('target')
const labelOf = (k) => items.find((i) => i.key === k)?.label || ''

const types = ref([])
onMounted(async () => {
  types.value = await loadCSV('통합돌봄-유형별.csv')
})

const gu = ['만세구', '효행구', '병점구', '동탄구']
const bars = [
  { label: '장기요양재가', data: [6255, 5838, 3753, 5003], color: '#f0a93a', stack: 'a' },
  { label: '퇴원환자', data: [595, 555, 357, 475], color: '#e45b5b', stack: 'a' },
  { label: '요양시설퇴소', data: [71, 67, 43, 57], color: '#2bc4c4', stack: 'a' },
  { label: '돌봄중점군', data: [173, 161, 104, 137], color: '#4da3ff', stack: 'a' },
  { label: '고령장애인', data: [761, 710, 457, 609], color: '#8b7ff0', stack: 'a' },
]
</script>

<template>
  <MenuLayout v-model="active" icon="people" title="바로이웃 통합돌봄" :items="items">
    <div class="view" v-if="active === 'target'">
      <div class="note">공개 집계값(개인정보 미수집) · 기준일 2025-12-31</div>

      <Card title="통합돌봄 대상자 현황">
        <StatTile label="우선관리 대상자" value="26,181명" icon="people" accent />
        <ul class="brk">
          <li v-for="r in types" :key="r['유형']">
            <Icon :name="r['아이콘']" :size="20" />
            <span class="t">{{ r['유형'] }}</span>
            <b class="n">{{ fmt(num(r['대상자수'])) }}명</b>
          </li>
        </ul>
      </Card>

      <Card title="통합돌봄 대상자 지원현황 (추진 실적)">
        <div class="two">
          <StatTile label="목표 대상자" value="1,750명" icon="people" />
          <StatTile label="추진 실적" value="1,350명" icon="chart-line" accent />
        </div>
        <div class="cap">기준일 2026-10-31</div>
      </Card>

      <Card title="구별 우선관리 대상자 현황 (집계)">
        <BarLineChart :labels="gu" :bars="bars" :height="320" />
        <div class="cap">구별 분포는 집계·추정</div>
      </Card>
    </div>

    <div class="view" v-else>
      <Card :title="labelOf(active)">
        <div class="cap">준비 중</div>
      </Card>
    </div>
  </MenuLayout>
</template>

<style scoped>
.view { display: flex; flex-direction: column; gap: 14px; }
.note, .cap { color: var(--muted); font-size: 12px; }
.cap { margin-top: 8px; }
.brk { list-style: none; margin: 12px 0 0; padding: 0; }
.brk li {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 4px; border-bottom: 1px solid var(--rule);
  color: var(--ink);
}
.brk li:last-child { border-bottom: 0; }
.brk .t { flex: 1; min-width: 0; }
.brk .n { margin-left: auto; text-align: right; font-weight: 700; color: var(--orange-hot); }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 560px) { .two { grid-template-columns: 1fr; } }
</style>
