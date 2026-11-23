<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import Icon from './Icon.vue'
const props = defineProps({ rows: Array, perPage: { type: Number, default: 4 }, interval: { type: Number, default: 4500 } })

// 지표 → 아이콘·색 매핑(원본 다모아 관측: GRDP=원, 고용률·종사자=사람, 아동=아기, 평균연령=가족, 그 외=톱니)
function mapIcon(ind = '') {
  if (ind.includes('아동') || ind.includes('출생')) return ['baby', '#ff9ab0']
  if (ind.includes('평균연령')) return ['family', '#8fb8ff']
  if (ind.includes('고용') || ind.includes('종사')) return ['people', '#8fb8ff']
  if (ind.includes('GRDP') || ind.includes('총생산')) return ['won', '#ffd166']
  return ['gear', '#35c6c6'] // 인구수·수출·사업체·제조업 등
}
function rankLabel(r) {
  const base = `${r['순위범위']} ${r['순위']}위`
  return r['비고'] ? `${base} (${r['비고']})` : base
}

const page = ref(0)
const pageCount = computed(() => Math.max(1, Math.ceil((props.rows?.length || 0) / props.perPage)))
const current = computed(() => (props.rows || []).slice(page.value * props.perPage, page.value * props.perPage + props.perPage))

let timer = null
function start() {
  stop()
  if (pageCount.value > 1) timer = setInterval(() => { page.value = (page.value + 1) % pageCount.value }, props.interval)
}
function stop() { if (timer) { clearInterval(timer); timer = null } }
onMounted(start)
onBeforeUnmount(stop)
watch(pageCount, start)
</script>

<template>
  <div class="stature">
    <div class="flip-wrap">
      <Transition name="flip" mode="out-in">
        <div class="st-grid" :key="page">
          <div v-for="(r, i) in current" :key="i" class="st-card">
            <div class="badge">
              <Icon :name="mapIcon(r['지표'])[0]" :size="28" :style="{ color: mapIcon(r['지표'])[1] }" />
            </div>
            <div class="info">
              <div class="rank">{{ rankLabel(r) }}</div>
              <div class="metric">{{ r['지표'] }}/<b>{{ r['값표기'] }}</b></div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
    <div v-if="pageCount > 1" class="dots">
      <button v-for="p in pageCount" :key="p" class="dot" :class="{ on: p - 1 === page }"
              @click="page = p - 1; start()" :aria-label="`${p}페이지`"></button>
    </div>
  </div>
</template>

<style scoped>
.stature { perspective: 1200px; }
.flip-wrap { position: relative; }
.st-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; transform-style: preserve-3d; }
.st-card {
  display: flex; align-items: center; gap: 12px;
  background: rgba(10,24,40,.55); border: 1px solid var(--rule);
  border-radius: 10px; padding: 16px 14px; min-height: 84px;
}
.badge {
  flex: 0 0 auto; width: 48px; height: 48px; border-radius: 50%;
  background: #0d1f33; border: 1px solid rgba(255,255,255,.08);
  display: flex; align-items: center; justify-content: center;
}
.info { min-width: 0; }
.rank { color: #fff; font-weight: 800; font-size: 1rem; }
.metric { color: var(--muted); font-size: .82rem; margin-top: 5px; line-height: 1.35; }
.metric b { color: #dfe8f2; font-weight: 700; }

/* 플립(회전) 전환 */
.flip-enter-active, .flip-leave-active { transition: transform .45s ease, opacity .45s ease; }
.flip-enter-from { transform: rotateX(-90deg); opacity: 0; transform-origin: top center; }
.flip-leave-to { transform: rotateX(90deg); opacity: 0; transform-origin: bottom center; }

.dots { display: flex; justify-content: center; gap: 7px; margin-top: 12px; }
.dot { width: 8px; height: 8px; border-radius: 50%; border: 0; padding: 0; cursor: pointer;
  background: rgba(255,255,255,.22); }
.dot.on { background: var(--orange-hot); }
</style>
