<script setup>
import { computed } from 'vue'
// 월 달력. year, month(1-12), events: [{day:int, title}]. 날짜 셀에 파란 이벤트 바.
const props = defineProps({
  year: { type: Number, required: true },
  month: { type: Number, required: true },
  events: { type: Array, default: () => [] }, // {day, title}
})
const DOW = ['일', '월', '화', '수', '목', '금', '토']
const weeks = computed(() => {
  const first = new Date(props.year, props.month - 1, 1)
  const startDow = first.getDay()
  const days = new Date(props.year, props.month, 0).getDate()
  const byDay = {}
  for (const e of props.events) (byDay[e.day] ||= []).push(e)
  const cells = []
  for (let i = 0; i < startDow; i++) cells.push(null)
  for (let d = 1; d <= days; d++) cells.push({ day: d, events: byDay[d] || [] })
  while (cells.length % 7) cells.push(null)
  const w = []
  for (let i = 0; i < cells.length; i += 7) w.push(cells.slice(i, i + 7))
  return w
})
</script>

<template>
  <div class="cal">
    <div class="cal-head">
      <div v-for="(d, i) in DOW" :key="d" class="dow" :class="{ sun: i === 0, sat: i === 6 }">{{ d }}</div>
    </div>
    <div v-for="(wk, wi) in weeks" :key="wi" class="week">
      <div v-for="(c, ci) in wk" :key="ci" class="cell" :class="{ empty: !c }">
        <template v-if="c">
          <div class="dnum" :class="{ sun: ci === 0, sat: ci === 6 }">{{ c.day }}</div>
          <div class="evs">
            <div v-for="(e, ei) in c.events" :key="ei" class="ev" :title="e.title">{{ e.title }}</div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cal { border: 1px solid var(--rule); border-radius: 8px; overflow: hidden; }
.cal-head, .week { display: grid; grid-template-columns: repeat(7, 1fr); }
.dow { text-align: center; padding: 10px 0; font-weight: 700; color: var(--muted);
  background: rgba(255,255,255,.04); border-bottom: 1px solid var(--rule); }
.dow.sun { color: #ff8a8a; } .dow.sat { color: #8ab4ff; }
.cell { min-height: 92px; padding: 6px; border-right: 1px solid var(--rule); border-bottom: 1px solid var(--rule); }
.cell:nth-child(7n) { border-right: 0; }
.cell.empty { background: rgba(0,0,0,.12); }
.dnum { font-size: .85rem; color: var(--ink); margin-bottom: 4px; }
.dnum.sun { color: #ff8a8a; } .dnum.sat { color: #8ab4ff; }
.evs { display: flex; flex-direction: column; gap: 3px; }
.ev { background: var(--blue); color: #fff; font-size: .72rem; padding: 2px 6px; border-radius: 4px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
@media (max-width: 760px) { .cell { min-height: 64px; } .ev { font-size: .64rem; } }
</style>
