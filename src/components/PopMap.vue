<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import L from 'leaflet'
const props = defineProps({ geo: Object, pop: Object, stations: Object })
const el = ref(null)
let map = null
let dataLayer = null
let stationLayer = null

const STOPS = ['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026']
function color(v, max) {
  if (!v || max <= 0) return '#cfd8e3'
  const r = Math.min(v / max, 1)
  return STOPS[Math.min(STOPS.length - 1, Math.floor(r * STOPS.length))]
}

function render() {
  if (!el.value || !props.geo) return
  if (!map) {
    map = L.map(el.value, { zoomControl: true, scrollWheelZoom: true }).setView([37.17, 126.92], 10)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18, attribution: '© OpenStreetMap',
    }).addTo(map)
  }
  if (dataLayer) { map.removeLayer(dataLayer); dataLayer = null }
  if (stationLayer) { map.removeLayer(stationLayer); stationLayer = null }

  const pm = {}
  if (props.pop?.status === 'ok') props.pop.dongs.forEach((d) => { pm[d.dong] = d.total })
  const max = Math.max(...Object.values(pm), 1)

  dataLayer = L.geoJSON(props.geo, {
    style: (f) => ({
      fillColor: color(pm[f.properties.dong] || 0, max),
      fillOpacity: 0.78, color: '#ffffff', weight: 1,
    }),
    onEachFeature: (f, layer) => {
      const n = pm[f.properties.dong] || 0
      layer.bindTooltip(`${f.properties.dong} · ${n.toLocaleString('ko-KR')}명`, { sticky: true })
    },
  }).addTo(map)
  map.fitBounds(dataLayer.getBounds(), { padding: [12, 12] })

  if (props.stations?.status === 'ok') {
    stationLayer = L.layerGroup(
      props.stations.stations.map((s) =>
        L.circleMarker([+s.lat, +s.lng], {
          radius: 5, color: '#167aff', weight: 2, fillColor: '#2c67df', fillOpacity: 0.9,
        }).bindTooltip(`측정소 ${s.station}`)),
    ).addTo(map)
  }
}

onMounted(render)
watch(() => [props.geo, props.pop, props.stations], render, { deep: false })
onBeforeUnmount(() => { if (map) { map.remove(); map = null } })
</script>

<template>
  <div ref="el" class="map"></div>
</template>

<style scoped>
.map { height: 760px; width: 100%; }
:deep(.leaflet-container) { background: #0c1b2e; font-family: inherit; }
</style>
