<script setup>
import Icon from './Icon.vue'
defineProps({ total: { type: String, default: '1,074,002' } })
</script>

<template>
  <section class="pop-card">
    <div class="label">인구</div>
    <div class="num">{{ total }}<span class="u">명</span></div>
    <div class="ico"><Icon name="users" :size="64" /></div>
  </section>
</template>

<style scoped>
.pop-card {
  position: relative; overflow: hidden; border-radius: var(--radius);
  padding: 16px 18px;
  background: linear-gradient(135deg, var(--orange-hot) 0%, var(--orange-hot) 58%, var(--peach) 100%);
  box-shadow: 0 8px 24px rgba(0,0,0,.25);
}
.label { color: #fff3ea; font-weight: 700; font-size: 1rem; }
.num { color: #fff; font-weight: 800; font-size: 2.15rem; letter-spacing: -.02em; margin-top: 4px; }
.u { font-size: 1.1rem; font-weight: 700; margin-left: 3px; }
.ico { position: absolute; right: 16px; top: 50%; transform: translateY(-50%); color: #fff; opacity: .26; }
</style>
