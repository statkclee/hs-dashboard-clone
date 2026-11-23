<script setup>
import { ref } from 'vue'
import TopNav from './components/TopNav.vue'
import HomeView from './components/HomeView.vue'
import StubView from './components/StubView.vue'

const MENUS = [
  { name: '홈', icon: 'house' },
  { name: '도시현황', icon: 'chart-line' },
  { name: '행정현황', icon: 'chart-column' },
  { name: '사업관리', icon: 'clipboard' },
  { name: '재난/안전', icon: 'shield' },
  { name: '교통', icon: 'car' },
  { name: '문화/관광', icon: 'landmark' },
  { name: '바로이웃 통합돌봄', icon: 'people' },
]
const active = ref('홈')
</script>

<template>
  <TopNav :menus="MENUS" :active="active" @select="active = $event" />
  <main class="page">
    <HomeView v-if="active === '홈'" />
    <StubView v-else :name="active" />
  </main>
</template>

<style>
.page { padding: 16px 20px 40px; max-width: 1920px; margin: 0 auto; }
</style>
