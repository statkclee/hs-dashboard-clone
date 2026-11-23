<script setup>
import { computed } from 'vue'
import { airGrade, SKY, PTY, num } from '../lib/data.js'
import DataTable from './DataTable.vue'
const props = defineProps({ wx: Object, air: Object })

const ok = computed(() => props.wx?.status === 'ok')
const airOk = computed(() => props.air?.status === 'ok')
const o3 = computed(() => {
  if (!airOk.value) return null
  const vs = props.air.stations.map((s) => num(s.o3)).filter((v) => v != null)
  return vs.length ? Math.round((vs.reduce((a, b) => a + b, 0) / vs.length) * 1000) / 1000 : null
})
const badges = computed(() => [
  { name: '초미세', v: props.air?.pm25_avg, g: airGrade('pm25', props.air?.pm25_avg), unit: '㎍/㎥' },
  { name: '미세', v: props.air?.pm10_avg, g: airGrade('pm10', props.air?.pm10_avg), unit: '㎍/㎥' },
  { name: '오존', v: o3.value, g: airGrade('o3', o3.value), unit: 'ppm' },
])
const stRows = computed(() =>
  airOk.value ? props.air.stations.map((s) => [s.station, s.pm10, s.pm25, s.o3]) : [])
</script>

<template>
  <section class="card wa-card">
    <div class="card-h">날씨 · 대기</div>
    <div class="card-b">
      <template v-if="ok">
        <p class="muted small">기준: {{ wx.collectedAt }}</p>

        <div class="temprow">
          <div class="now">
            <div><span class="big">{{ wx.tempC }}</span><span class="bigu">°C</span></div>
            <div class="cap">현재기온</div>
          </div>
          <div class="mmbox"><div class="cap">최저</div><div class="mm min">{{ wx.tmin ?? '—' }}°</div></div>
          <div class="mmbox"><div class="cap">최고</div><div class="mm max">{{ wx.tmax ?? '—' }}°</div></div>
        </div>

        <div class="condrow">
          <div class="cond"><div class="cap">하늘</div><div class="cv">{{ SKY[String(wx.sky)] || '—' }}</div></div>
          <div class="cond"><div class="cap">강수</div><div class="cv">{{ PTY[String(wx.pty)] || '—' }}</div></div>
          <div class="cond"><div class="cap">강수확률</div><div class="cv">{{ wx.pop ?? '—' }}%</div></div>
        </div>

        <div class="sec">대기 현황</div>
        <div class="aq-row">
          <div v-for="b in badges" :key="b.name" class="aq">
            <div class="emo">{{ b.g[2] }}</div>
            <div class="line"><span class="aname">{{ b.name }}</span><span class="grade" :style="{ background: b.g[1] }">{{ b.g[0] }}</span></div>
            <div><span class="aval">{{ b.v ?? '—' }}</span><span class="aunit">{{ b.unit }}</span></div>
          </div>
        </div>

        <div class="sec">기상</div>
        <div class="envrow">
          <div class="env"><div class="cap">습도</div><div class="ev">{{ wx.humidity ?? '—' }}%</div></div>
          <div class="env"><div class="cap">풍속</div><div class="ev">{{ wx.windSpeed ?? '—' }} ㎧</div></div>
          <div class="env"><div class="cap">강수량</div><div class="ev">{{ wx.precip ?? '—' }}</div></div>
        </div>

        <template v-if="stRows.length">
          <div class="sec">측정소별 실시간</div>
          <DataTable :cols="['측정소', '미세', '초미세', '오존']" :rows="stRows" />
        </template>

        <p class="muted small note">키는 서버에만 · 방문자 수와 무관하게 서버가 주기 수집(원본 429 문제 제거).</p>
      </template>
      <template v-else>
        <p class="collect-note">서버 수집 대기 — 인증키가 서버에 설정되면 매시 수집(키는 서버에만).</p>
      </template>
    </div>
  </section>
</template>

<style scoped>
.wa-card .card-h { border-left-color: var(--blue2); }
.cap { color: var(--muted); font-size: .76rem; }
.temprow { display: flex; gap: 10px; margin: 8px 0 6px; }
.now { flex: 1.3; background: rgba(44,103,223,.14); border: 1px solid var(--rule);
  border-radius: 10px; padding: 10px 14px; display: flex; flex-direction: column; justify-content: center; }
.big { font-size: 2.6rem; font-weight: 800; color: #fff; line-height: 1; }
.bigu { font-size: 1.1rem; color: var(--muted); margin-left: 2px; }
.mmbox { flex: 1; background: rgba(255,255,255,.04); border: 1px solid var(--rule);
  border-radius: 10px; padding: 10px; text-align: center; display: flex; flex-direction: column; justify-content: center; }
.mm { font-size: 1.5rem; font-weight: 800; }
.min { color: #6db6ff; } .max { color: #ff9a6b; }
.condrow, .envrow { display: flex; gap: 10px; margin: 6px 0; }
.cond, .env { flex: 1; background: rgba(255,255,255,.04); border: 1px solid var(--rule);
  border-radius: 8px; padding: 8px 10px; text-align: center; }
.cv, .ev { color: #fff; font-weight: 700; font-size: .98rem; margin-top: 2px; }
.sec { color: #fff; font-weight: 700; font-size: .9rem; margin: 14px 0 7px;
  padding-left: 8px; border-left: 3px solid var(--orange-hot); }
.aq-row { display: flex; gap: 10px; }
.aq { flex: 1; background: rgba(255,255,255,.04); border: 1px solid var(--rule);
  border-radius: 10px; padding: 10px; text-align: center; }
.emo { font-size: 1.5rem; }
.line { margin: 2px 0; }
.aname { color: var(--muted); font-size: .82rem; margin-right: 5px; }
.grade { color: #fff; font-size: .72rem; font-weight: 700; padding: 1px 7px; border-radius: 9px; }
.aval { color: #fff; font-weight: 800; font-size: 1.15rem; }
.aunit { color: var(--muted); font-size: .72rem; margin-left: 2px; }
.note { margin-top: 10px; }
</style>
