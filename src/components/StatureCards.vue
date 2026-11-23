<script setup>
import Icon from './Icon.vue'
defineProps({ rows: Array })

// 지표 → 아이콘·색 매핑(원본: 원형 아이콘 배지)
function mapIcon(ind = '') {
  if (ind.includes('아동') || ind.includes('출생')) return ['baby', '#ff9ab0']
  if (ind.includes('수출')) return ['gear', '#35c6c6']
  if (ind.includes('고용')) return ['briefcase', '#ffcf6b']
  if (ind.includes('사업체')) return ['building', '#9fd3ff']
  if (ind.includes('GRDP') || ind.includes('총생산')) return ['won', '#ffd166']
  if (ind.includes('종사')) return ['family', '#8fb8ff']
  if (ind.includes('평균연령') || ind.includes('젊')) return ['family', '#8fb8ff']
  return ['family', '#8fb8ff'] // 인구수 등
}
</script>

<template>
  <div class="st-grid">
    <div v-for="(r, i) in rows" :key="i" class="st-card">
      <div class="badge">
        <Icon :name="mapIcon(r['지표'])[0]" :size="28" :style="{ color: mapIcon(r['지표'])[1] }" />
      </div>
      <div class="info">
        <div class="rank">{{ r['순위범위'] }} {{ r['순위'] }}위</div>
        <div class="metric">{{ r['지표'] }}/<b>{{ r['값표기'] }}</b></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.st-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.st-card {
  display: flex; align-items: center; gap: 12px;
  background: rgba(10,24,40,.55); border: 1px solid var(--rule);
  border-radius: 10px; padding: 14px 14px;
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
</style>
