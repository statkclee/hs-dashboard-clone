<script setup>
import Icon from './Icon.vue'
defineProps({ total: { type: String, default: '1,074,002' } })
</script>

<template>
  <section class="pop-card">
    <div class="head">인구</div>
    <div class="body">
      <div class="num">{{ total }}<span class="u">명</span></div>
      <div class="figs">
        <Icon name="users" :size="92" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.pop-card { border-radius: var(--radius); overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,.25); }
/* 원본: 밝은 오렌지 헤더 */
.head {
  background: var(--orange-hot); color: #fff; font-weight: 800; font-size: 1.1rem;
  text-align: center; padding: 10px 0; letter-spacing: .02em;
}
/* 원본: 어두운 갈색-오렌지 바디 + 실루엣 */
.body {
  position: relative; overflow: hidden;
  background: linear-gradient(160deg, #a5532a 0%, #7c3f20 100%);
  padding: 22px 20px; min-height: 92px; display: flex; align-items: center;
}
.num { color: #fff; font-weight: 800; font-size: 2.3rem; letter-spacing: -.02em; z-index: 1; }
.u { font-size: 1.1rem; font-weight: 700; margin-left: 3px; }
.figs { position: absolute; right: 10px; bottom: -14px; color: #fff; opacity: .22; }
</style>
