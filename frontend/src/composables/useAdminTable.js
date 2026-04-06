import { ref } from 'vue'

/**
 * 管理后台表格页共用 composable
 * 封装分页、加载、筛选逻辑
 *
 * @param {Function} fetchFn - 异步获取函数，接收 { page, page_size, ...extraParams }，返回 { items, total }
 */
export function useAdminTable(fetchFn) {
  const loading = ref(false)
  const error = ref(null)
  const items = ref([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const extraParams = ref({})

  async function fetchData() {
    loading.value = true
    error.value = null
    try {
      const res = await fetchFn({
        page: page.value,
        page_size: pageSize.value,
        ...extraParams.value
      })
      items.value = res.items || []
      total.value = res.total || 0
    } catch (e) {
      error.value = e.message || 'Load failed'
    } finally {
      loading.value = false
    }
  }

  function handlePageChange(newPage) {
    page.value = newPage
    fetchData()
  }

  function handlePageSizeChange(newSize) {
    pageSize.value = newSize
    page.value = 1
    fetchData()
  }

  function updateFilters(params) {
    extraParams.value = { ...extraParams.value, ...params }
    page.value = 1
    fetchData()
  }

  function refresh() {
    fetchData()
  }

  return {
    loading,
    error,
    items,
    total,
    page,
    pageSize,
    fetchData,
    handlePageChange,
    handlePageSizeChange,
    updateFilters,
    refresh
  }
}
