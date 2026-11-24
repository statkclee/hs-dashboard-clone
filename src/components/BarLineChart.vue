<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { Chart } from '../lib/chartSetup.js'
// 막대 여러 개 + 선 하나 조합. labels, bars:[{label,data,color}], line:{label,data,color}
const props = defineProps({
  labels: { type: Array, default: () => [] },
  bars: { type: Array, default: () => [] },
  line: { type: Object, default: null },
  height: { type: Number, default: 300 },
})
const el = ref(null)
let chart = null
function render() {
  if (!el.value) return
  if (chart) chart.destroy()
  const datasets = props.bars.map((b) => ({
    type: 'bar', label: b.label, data: b.data, backgroundColor: b.color, stack: b.stack, borderRadius: 3, order: 2,
  }))
  if (props.line) datasets.push({
    type: 'line', label: props.line.label, data: props.line.data,
    borderColor: props.line.color || '#a78bfa', backgroundColor: props.line.color || '#a78bfa',
    tension: 0.35, pointRadius: 2, borderWidth: 2, order: 1,
  })
  chart = new Chart(el.value, {
    data: { labels: props.labels, datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      scales: {
        x: { grid: { display: false }, ticks: { maxRotation: 60, minRotation: 45, font: { size: 10 } } },
        y: { grid: { color: 'rgba(255,255,255,.08)' }, ticks: { font: { size: 10 } } },
      },
      plugins: { legend: { position: 'top', labels: { font: { size: 11 } } } },
    },
  })
}
onMounted(render)
watch(() => [props.labels, props.bars, props.line], render, { deep: true })
onBeforeUnmount(() => { if (chart) chart.destroy() })
</script>

<template>
  <div :style="{ height: height + 'px' }"><canvas ref="el"></canvas></div>
</template>
