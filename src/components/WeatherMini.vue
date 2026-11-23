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
  <section class="card wcard">
    <div class="card-h"><Icon name="pin" :size="15" /> 화성시</div>
    <div class="card-b">
      <template v-if="ok">
        <div class="temp-row">
          <span class="temp">{{ wx.tempC }}</span><span class="unit">°C</span>
          <span class="sky">{{ sky }}</span>
        </div>
        <div class="badges">
          <div><span class="lab">초미세</span><span class="badge" :style="{ background: pm25[1] }">{{ pm25[0] }}</span></div>
          <div><span class="lab">미세</span><span class="badge" :style="{ background: pm10[1] }">{{ pm10[0] }}</span></div>
        </div>
      </template>
      <template v-else>
        <div class="temp">— °C</div>
        <p class="collect-note">서버 수집 대기 — 키는 서버에만.</p>
      </template>
    </div>
  </section>
</template>

<style scoped>
.temp-row { display: flex; align-items: baseline; gap: 2px; }
.temp { font-size: 2.5rem; font-weight: 800; color: #fff; line-height: 1; }
.unit { font-size: 1.1rem; color: var(--muted); }
.sky { margin-left: 10px; color: var(--muted); font-size: .98rem; align-self: center; }
.badges { display: flex; gap: 14px; margin-top: 12px; }
.badges > div { display: flex; align-items: center; gap: 7px; }
.lab { color: var(--muted); font-size: .86rem; }
.badge { color: #fff; font-weight: 700; font-size: .78rem; padding: 2px 9px; border-radius: 10px; }
</style>
