import { ref, watch, onMounted, onUnmounted } from 'vue'

const DRAFT_KEY = 'post_draft'
const SAVE_INTERVAL = 30000 // 30秒

export function useDraft() {
  const draft = ref({
    community_id: null,
    title: '',
    content: ''
  })
  const hasDraft = ref(false)
  let saveInterval = null

  // 加载草稿
  const loadDraft = () => {
    try {
      const saved = localStorage.getItem(DRAFT_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        draft.value = parsed
        hasDraft.value = true
        return parsed
      }
    } catch (error) {
      console.error('加载草稿失败:', error)
    }
    return null
  }

  // 保存草稿
  const saveDraft = (data) => {
    try {
      localStorage.setItem(DRAFT_KEY, JSON.stringify(data))
      draft.value = data
      hasDraft.value = true
      console.log('[草稿] 已保存')
    } catch (error) {
      console.error('保存草稿失败:', error)
    }
  }

  // 清除草稿
  const clearDraft = () => {
    localStorage.removeItem(DRAFT_KEY)
    draft.value = {
      community_id: null,
      title: '',
      content: ''
    }
    hasDraft.value = false
    console.log('[草稿] 已清除')
  }

  // 自动保存
  const startAutoSave = (formData) => {
    // 监听表单数据变化
    watch(formData, (newData) => {
      saveDraft(newData)
    }, { deep: true })

    // 定时保存
    saveInterval = setInterval(() => {
      saveDraft(formData)
    }, SAVE_INTERVAL)
  }

  const stopAutoSave = () => {
    if (saveInterval) {
      clearInterval(saveInterval)
      saveInterval = null
      console.log('[草稿] 停止自动保存')
    }
  }

  return {
    draft,
    hasDraft,
    loadDraft,
    saveDraft,
    clearDraft,
    startAutoSave,
    stopAutoSave
  }
}
