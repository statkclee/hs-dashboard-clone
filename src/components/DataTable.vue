<script setup>
defineProps({ cols: Array, rows: Array })
</script>

<template>
  <div class="tbl-wrap">
    <table class="tbl">
      <thead>
        <tr><th v-for="c in cols" :key="c">{{ c }}</th></tr>
      </thead>
      <tbody>
        <tr v-for="(r, i) in rows" :key="i">
          <td v-for="(cell, j) in r" :key="j">{{ cell === null || cell === undefined || cell === '' ? '—' : cell }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.tbl-wrap { overflow-x: auto; }
</style>
