<script setup>
defineProps({ name: String })
</script>

<template>
  <div class="card">
    <div class="card-h">{{ name }}</div>
    <div class="card-b">
      <p class="muted">{{ name }} 화면 — Vue 재구축 중(6-6). 데이터는 이미 수집돼 있어 곧 연결됩니다.</p>
    </div>
  </div>
</template>
