import { defineStore } from 'pinia'
import { useDark, useToggle } from '@vueuse/core'

export const useThemeStore = defineStore('theme', () => {
  // 使用 VueUse 的 useDark 管理主题
  const isDark = useDark({
    storageKey: 'theme',
    valueDark: 'dark',
    valueLight: 'light',
    selector: 'html',
    attribute: 'data-theme'
  })

  // 使用 useToggle 创建切换函数
  const toggleTheme = useToggle(isDark)

  return {
    isDark,
    toggleTheme
  }
})
