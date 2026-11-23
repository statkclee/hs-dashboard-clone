<script setup>
import { computed } from 'vue'
import { airGrade, SKY } from '../lib/data.js'
import Icon from './Icon.vue'
const props = defineProps({ wx: Object, air: Object })

const ok = computed(() => props.wx?.status === 'ok')
const sky = computed(() => SKY[String(props.wx?.sky)] || '')
const pm25 = computed(() => airGrade('pm25', props.air?.pm25_avg))
const pm10 = computed(() => airGrade('pm10', props.air?.pm10_avg))
</script>

<template>
  <section class="card">
    <div class="card-h"><Icon name="pin" :size="15" /> 화성시</div>
    <div class="card-b">
      <!-- 파란 기온 패널 + 구름 -->
      <div class="temp-panel">
        <svg class="cloud" viewBox="0 0 120 70" aria-hidden="true">
          <g fill="#ffffff" opacity="0.10">
            <circle cx="40" cy="42" r="18" /><circle cx="62" cy="34" r="22" />
            <circle cx="84" cy="44" r="16" /><rect x="40" y="44" width="46" height="18" rx="9" />
          </g>
        </svg>
        <div class="temp">
          <template v-if="ok"><span class="t">{{ wx.tempC }}</span><span class="u">°C</span></template>
          <template v-else><span class="u big">°C</span></template>
        </div>
        <div v-if="ok && sky" class="sky">{{ sky }}</div>
      </div>
      <!-- 등급 알약 -->
      <div class="rows">
        <div class="r"><span class="lab">초미세먼지</span><span class="pill" :style="{ background: pm25[1] }">{{ pm25[0] }}</span></div>
        <div class="r"><span class="lab">미세먼지</span><span class="pill" :style="{ background: pm10[1] }">{{ pm10[0] }}</span></div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.temp-panel {
  position: relative; overflow: hidden;
  background: linear-gradient(160deg, #2f5fa6 0%, #244c87 100%);
  border-radius: 8px; height: 104px; margin-bottom: 14px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.cloud { position: absolute; left: 50%; bottom: 0; transform: translateX(-50%); width: 150px; height: 88px; }
.temp { display: flex; align-items: baseline; gap: 2px; z-index: 1; }
.temp .t { font-size: 2.6rem; font-weight: 800; color: #fff; line-height: 1; }
.temp .u { font-size: 1.2rem; color: #dce8f7; font-weight: 700; }
.temp .u.big { font-size: 1.7rem; }
.sky { color: #cfe0f5; font-size: .9rem; margin-top: 4px; z-index: 1; }
.rows { display: flex; flex-direction: column; gap: 9px; }
.r { display: flex; align-items: center; justify-content: space-between; }
.lab { color: var(--ink); font-size: .95rem; font-weight: 600; }
.pill { color: #fff; font-weight: 700; font-size: .82rem; padding: 3px 14px; border-radius: 12px; min-width: 54px; text-align: center; }
</style>
