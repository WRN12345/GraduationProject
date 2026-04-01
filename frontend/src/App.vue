<script setup>
import Layout from './components/Layout.vue'
import { useThemeStore } from '@/stores/theme'

// 初始化主题
const themeStore = useThemeStore()
</script>

<template>
  <router-view />
</template>

<style>
/* === 主题 CSS 变量（唯一来源） === */
:root {
  /* 主色调 */
  --color-primary: #0079d3;
  --color-primary-light: #00a0ff;
  --color-primary-bg: #f0f7ff;

  /* 背景色 */
  --bg-primary: #ffffff;
  --bg-secondary: #f6f7f8;
  --bg-tertiary: #f0f0f0;
  --bg-hover: #f5f5f5;
  --bg-active: #f0f7ff;
  --bg-card: #ffffff;
  --bg-input: #ffffff;

  /* 文字颜色 */
  --text-primary: #1c1c1c;
  --text-secondary: #666666;
  --text-tertiary: #999999;
  --text-inverse: #ffffff;

  /* 边框 */
  --border-color: #e8e8e8;
  --border-color-light: #edeff1;
  --border-light: #edeff1;

  /* 阴影 */
  --shadow-color: rgba(0, 0, 0, 0.1);
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.12);

  /* 滚动条 */
  --scrollbar-thumb: #cccccc;
  --scrollbar-track: transparent;

  /* 其他 */
  --overlay-bg: rgba(0, 0, 0, 0.4);

  /* 兼容别名（供 dark-mode.css 和组件使用） */
  --card-bg: var(--bg-card);
  --input-bg: var(--bg-input);
}

/* 深色模式变量 */
[data-theme="dark"] {
  /* 主色调 */
  --color-primary: #5ba3e6;
  --color-primary-light: #7db9f0;
  --color-primary-bg: #1a2a3a;

  /* 背景色 */
  --bg-primary: #1a1a2e;
  --bg-secondary: #222240;
  --bg-tertiary: #2a2a4a;
  --bg-hover: #2a2a4a;
  --bg-active: #1a2a3a;
  --bg-card: #222240;
  --bg-input: #2a2a4a;

  /* 文字颜色 */
  --text-primary: #e0e0e0;
  --text-secondary: #a0a0b0;
  --text-tertiary: #707080;
  --text-inverse: #1a1a2e;

  /* 边框 */
  --border-color: #333355;
  --border-color-light: #2a2a4a;
  --border-light: #2a2a4a;

  /* 阴影 */
  --shadow-color: rgba(0, 0, 0, 0.3);
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.5);

  /* 滚动条 */
  --scrollbar-thumb: #444466;
  --scrollbar-track: transparent;

  /* 其他 */
  --overlay-bg: rgba(0, 0, 0, 0.6);

  /* 兼容别名 */
  --card-bg: var(--bg-card);
  --input-bg: var(--bg-input);
}

/* 全局重置与背景色 */
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 0.3s ease, color 0.3s ease;
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

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 4px;
}
::-webkit-scrollbar-track {
  background: var(--scrollbar-track);
}
</style>
