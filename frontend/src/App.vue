<script setup>
import Layout from './components/Layout.vue'
</script>

<template>
  <router-view />
</template>

<style>
/* 全局重置与背景色 */
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: #e0e5e9; 
  color: #1c1c1c;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

a {
  text-decoration: none;
  color: inherit;
}

/* 滚动条美化 (可选) */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}
</style>