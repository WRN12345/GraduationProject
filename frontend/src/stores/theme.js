import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref(localStorage.getItem('theme') || 'light')

  const isDark = () => theme.value === 'dark'

  const applyTheme = (newTheme) => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)

    if (newTheme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark')
    } else {
      document.documentElement.removeAttribute('data-theme')
    }
  }

  const toggleTheme = () => {
    applyTheme(isDark() ? 'light' : 'dark')
  }

  // 初始化时应用主题
  applyTheme(theme.value)

  return {
    theme,
    isDark,
    applyTheme,
    toggleTheme
  }
})
