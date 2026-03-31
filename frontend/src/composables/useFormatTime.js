import { useI18n } from 'vue-i18n'

export function useFormatTime() {
  const { t } = useI18n()

  const formatTime = (dateString) => {
    if (!dateString) return t('common.unknownTime')
    const date = new Date(dateString)
    const now = new Date()
    const diff = (now - date) / 1000 // 秒

    if (diff < 60) return t('common.justNow')
    if (diff < 3600) return t('common.minutesAgo', { n: Math.floor(diff / 60) })
    if (diff < 86400) return t('common.hoursAgo', { n: Math.floor(diff / 3600) })
    if (diff < 604800) return t('common.daysAgo', { n: Math.floor(diff / 86400) })

    return date.toLocaleDateString()
  }

  return { formatTime }
}
