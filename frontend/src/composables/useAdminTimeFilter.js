import { ref, computed } from 'vue'

const selectedRange = ref('7d')
const customStartDate = ref(null)
const customEndDate = ref(null)

export function useAdminTimeFilter() {
  const timeRange = computed(() => {
    const now = new Date()
    switch (selectedRange.value) {
      case '24h': {
        const dayAgo = new Date(now.getTime() - 86400000)
        return { start: dayAgo, end: now, days: 1 }
      }
      case '7d': {
        const weekAgo = new Date(now.getTime() - 7 * 86400000)
        return { start: weekAgo, end: now, days: 7 }
      }
      case '30d': {
        const monthAgo = new Date(now.getTime() - 30 * 86400000)
        return { start: monthAgo, end: now, days: 30 }
      }
      case 'custom':
        return {
          start: customStartDate.value,
          end: customEndDate.value,
          days: null
        }
      default:
        return { start: null, end: null, days: null }
    }
  })

  function setRange(range) {
    selectedRange.value = range
  }

  function setCustomRange(start, end) {
    customStartDate.value = start
    customEndDate.value = end
    selectedRange.value = 'custom'
  }

  function getDaysParam() {
    if (selectedRange.value === 'custom') return null
    return timeRange.value.days
  }

  function getDateParams() {
    return {
      start_date: timeRange.value.start?.toISOString().split('T')[0],
      end_date: timeRange.value.end?.toISOString().split('T')[0]
    }
  }

  return {
    selectedRange,
    timeRange,
    setRange,
    setCustomRange,
    getDaysParam,
    getDateParams
  }
}
