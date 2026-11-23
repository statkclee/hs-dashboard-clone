<script setup>
defineProps({ title: String, accent: String })
</script>

<template>
  <section class="card">
    <div class="card-h" :style="accent ? { borderLeftColor: accent } : {}">
      <slot name="title">{{ title }}</slot>
    </div>
    <div class="card-b"><slot /></div>
  </section>
</template>
