<script setup>
import Icon from './Icon.vue'
const base = import.meta.env.BASE_URL || './'
defineProps({ menus: Array, active: String })
const emit = defineEmits(['select'])
</script>

<template>
  <header class="topnav">
    <a class="brand" @click.prevent="emit('select', menus[0].name)" href="#">
      <img :src="`${base}logo.png`" alt="모두의 행복 더큰 화성" class="logo" />
    </a>
    <nav class="menu">
      <a
        v-for="m in menus" :key="m.name" href="#"
        class="item" :class="{ active: active === m.name }"
        @click.prevent="emit('select', m.name)"
      >
        <Icon :name="m.icon" :size="17" />
        <span>{{ m.name }}</span>
      </a>
      <a
        class="item ext"
        href="https://total.hscity.go.kr/web2/dashboard-main/shares/415bf387db01b77eb8d2f6ae700b8934"
        target="_blank" rel="noopener noreferrer"
        title="원본 다모아 플랫폼 (새 탭)"
      >
        <img :src="`${base}favicon.png`" class="favi" alt="화성시" />
        <span>원본 다모아 바로가기</span>
        <span class="arr" aria-hidden="true">↗</span>
      </a>
    </nav>
  </header>
</template>

<style scoped>
.topnav {
  display: flex; align-items: center; gap: 18px;
  height: 56px; padding: 0 20px;
  background: #122a44;
  border-bottom: 1px solid var(--rule);
  position: sticky; top: 0; z-index: 50;
}
.brand { display: flex; align-items: center; height: 100%; }
.logo { height: 38px; display: block; mix-blend-mode: lighten; }
.menu { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.item {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 7px 13px; border-radius: 8px;
  color: #d2deec; font-weight: 600; font-size: .95rem;
  text-decoration: none; white-space: nowrap;
  border-bottom: 2px solid transparent;
}
.item:hover { color: #fff; background: rgba(255,255,255,.05); }
.item.active { color: #fff; border-bottom-color: var(--blue); }
.item .ico { opacity: .95; }
.item.ext { margin-left: auto; border: 1px solid rgba(255,255,255,.18); background: rgba(255,138,46,.14); }
.item.ext:hover { background: rgba(255,138,46,.26); border-color: var(--orange-hot); }
.favi { width: 18px; height: 18px; border-radius: 3px; display: block; }
.item.ext .arr { opacity: .8; font-size: .9rem; }
@media (max-width: 900px) { .item.ext { margin-left: 0; } }
</style>
