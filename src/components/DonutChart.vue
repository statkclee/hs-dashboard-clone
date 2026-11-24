<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { Chart } from '../lib/chartSetup.js'
// 가운데 퍼센트 표시 도넛. props.percent(0~100), color.
const props = defineProps({
  percent: { type: Number, default: 0 },
  color: { type: String, default: '#167aff' },
  track: { type: String, default: 'rgba(255,255,255,.12)' },
  size: { type: [Number, String], default: 150 },
  label: String,
})
const el = ref(null)
let chart = null
const centerText = {
  id: 'centerText',
  afterDraw(c) {
    const { ctx, chartArea } = c
    if (!chartArea) return
    const x = (chartArea.left + chartArea.right) / 2
    const y = (chartArea.top + chartArea.bottom) / 2
    ctx.save()
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle'
    ctx.fillStyle = '#fff'
    ctx.font = '700 ' + Math.round(c.height * 0.2) + 'px Pretendard, sans-serif'
    ctx.fillText((props.percent ?? 0) + '%', x, props.label ? y - 8 : y)
    if (props.label) {
      ctx.fillStyle = '#9fb3c8'; ctx.font = '400 11px Pretendard, sans-serif'
      ctx.fillText(props.label, x, y + 12)
    }
    ctx.restore()
  },
}
function render() {
  if (!el.value) return
  if (chart) chart.destroy()
  const p = Math.max(0, Math.min(100, props.percent || 0))
  chart = new Chart(el.value, {
    type: 'doughnut',
    data: { datasets: [{ data: [p, 100 - p], backgroundColor: [props.color, props.track], borderWidth: 0 }] },
    options: { cutout: '72%', responsive: true, maintainAspectRatio: true,
      plugins: { legend: { display: false }, tooltip: { enabled: false } } },
    plugins: [centerText],
  })
}
onMounted(render)
watch(() => [props.percent, props.color], render)
onBeforeUnmount(() => { if (chart) chart.destroy() })
</script>

<template>
  <div class="donut" :style="{ width: size + 'px', height: size + 'px' }"><canvas ref="el"></canvas></div>
</template>

<style scoped>
.donut { position: relative; }
</style>
