<script setup>
import { computed } from 'vue'
// 대기질 등급 스마일(원본 다모아는 캔버스 렌더라 파일 추출 불가 → 동일 스타일 SVG 재현)
const props = defineProps({ grade: { type: Number, default: 0 }, color: String, size: { type: [Number, String], default: 30 } })
const mouth = computed(() => [
  'M12 24 Q20 32 28 24',   // 좋음: 큰 미소
  'M13 25 Q20 29 27 25',   // 보통: 미소
  'M13 27 H27',            // 나쁨: 일자
  'M12 29 Q20 23 28 29',   // 매우나쁨: 찡그림
][props.grade] || 'M13 26 H27')
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 40 40" class="face">
    <circle cx="20" cy="20" r="18" :fill="color" />
    <template v-if="grade < 3">
      <circle cx="14" cy="16.5" r="2.1" fill="#fff" />
      <circle cx="26" cy="16.5" r="2.1" fill="#fff" />
    </template>
    <template v-else>
      <path d="M12 14.5 L16 18.5 M16 14.5 L12 18.5" stroke="#fff" stroke-width="2" stroke-linecap="round" />
      <path d="M24 14.5 L28 18.5 M28 14.5 L24 18.5" stroke="#fff" stroke-width="2" stroke-linecap="round" />
    </template>
    <path :d="mouth" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round" />
  </svg>
</template>

<style scoped>
.face { display: block; filter: drop-shadow(0 2px 4px rgba(0,0,0,.25)); }
</style>
