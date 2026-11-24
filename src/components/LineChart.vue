<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { Chart } from '../lib/chartSetup.js'
// 여러 선. labels, series:[{label,data,color}]
const props = defineProps({
  labels: { type: Array, default: () => [] },
  series: { type: Array, default: () => [] },
  height: { type: Number, default: 260 },
})
const el = ref(null)
let chart = null
function render() {
  if (!el.value) return
  if (chart) chart.destroy()
  chart = new Chart(el.value, {
    type: 'line',
    data: {
      labels: props.labels,
      datasets: props.series.map((s) => ({
        label: s.label, data: s.data, borderColor: s.color, backgroundColor: s.color,
        tension: 0.35, pointRadius: 2, borderWidth: 2, fill: false,
      })),
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 10 } } },
        y: { grid: { color: 'rgba(255,255,255,.08)' }, ticks: { font: { size: 10 } } },
      },
      plugins: { legend: { position: 'top', labels: { font: { size: 11 } } } },
    },
  })
}
onMounted(render)
watch(() => [props.labels, props.series], render, { deep: true })
onBeforeUnmount(() => { if (chart) chart.destroy() })
</script>

<template>
  <div :style="{ height: height + 'px' }"><canvas ref="el"></canvas></div>
</template>
