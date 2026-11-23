<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
const now = ref('')
let timer = null
const p = (n) => String(n).padStart(2, '0')
function tick() {
  const d = new Date()
  const ap = d.getHours() < 12 ? '오전' : '오후'
  let h = d.getHours() % 12
  if (h === 0) h = 12
  now.value = `${d.getFullYear()}. ${p(d.getMonth() + 1)}. ${p(d.getDate())}. ${ap} ${p(h)}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}
onMounted(() => { tick(); timer = setInterval(tick, 1000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <div class="datebar">{{ now }}</div>
</template>

<style scoped>
.datebar {
  background: rgba(10,24,40,.7);
  border: 1.5px solid var(--orange-hot);
  border-radius: 8px;
  color: #fff; font-weight: 800; font-size: .98rem;
  text-align: center; padding: 11px 0; letter-spacing: .3px;
}
</style>
