import { ref, watch, onMounted, onUnmounted } from 'vue'
import { client } from '@/api/client'

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

  // 加载本地草稿
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

  // 保存本地草稿
  const saveDraft = (data) => {
    try {
      localStorage.setItem(DRAFT_KEY, JSON.stringify(data))
      draft.value = data
      hasDraft.value = true
      console.log('[草稿] 已保存到本地')
    } catch (error) {
      console.error('保存草稿失败:', error)
    }
  }

  // 清除本地草稿
  const clearDraft = () => {
    localStorage.removeItem(DRAFT_KEY)
    draft.value = {
      community_id: null,
      title: '',
      content: ''
    }
    hasDraft.value = false
    console.log('[草稿] 已清除本地草稿')
  }

  // 自动保存
  const startAutoSave = (formData) => {
    watch(formData, (newData) => {
      saveDraft(newData)
    }, { deep: true })

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

  // ========== 服务端草稿方法 ==========

  // 保存草稿到服务端
  const saveDraftToServer = async (data) => {
    try {
      const response = await client.POST('/v1/drafts', {
        body: {
          title: data.title || '',
          content: data.content || '',
          community_id: data.community_id || null,
          attachment_ids: data.attachment_ids || []
        }
      })

      if (response.error) {
        console.error('[草稿] 保存到服务端失败:', response.error)
        return { error: response.error }
      }

      console.log('[草稿] 已保存到服务端, ID:', response.data.id)
      return { data: response.data }
    } catch (error) {
      console.error('[草稿] 保存到服务端异常:', error)
      return { error: error.message }
    }
  }

  // 更新服务端草稿
  const updateDraftToServer = async (draftId, data) => {
    try {
      const response = await client.PUT('/v1/drafts/{draft_id}', {
        params: {
          path: { draft_id: draftId }
        },
        body: {
          title: data.title,
          content: data.content,
          community_id: data.community_id,
          attachment_ids: data.attachment_ids
        }
      })

      if (response.error) {
        console.error('[草稿] 更新服务端草稿失败:', response.error)
        return { error: response.error }
      }

      console.log('[草稿] 已更新服务端草稿, ID:', draftId)
      return { data: response.data }
    } catch (error) {
      console.error('[草稿] 更新服务端草稿异常:', error)
      return { error: error.message }
    }
  }

  // 获取服务端草稿列表
  const fetchDraftsFromServer = async (skip = 0, limit = 20) => {
    try {
      const response = await client.GET('/v1/drafts', {
        params: {
          query: { skip, limit }
        }
      })

      if (response.error) {
        console.error('[草稿] 获取草稿列表失败:', response.error)
        return { error: response.error }
      }

      return { data: response.data }
    } catch (error) {
      console.error('[草稿] 获取草稿列表异常:', error)
      return { error: error.message }
    }
  }

  // 获取服务端草稿详情
  const fetchDraftDetail = async (draftId) => {
    try {
      const response = await client.GET('/v1/drafts/{draft_id}', {
        params: {
          path: { draft_id: draftId }
        }
      })

      if (response.error) {
        console.error('[草稿] 获取草稿详情失败:', response.error)
        return { error: response.error }
      }

      return { data: response.data }
    } catch (error) {
      console.error('[草稿] 获取草稿详情异常:', error)
      return { error: error.message }
    }
  }

  // 删除服务端草稿
  const deleteDraftFromServer = async (draftId) => {
    try {
      const response = await client.DELETE('/v1/drafts/{draft_id}', {
        params: {
          path: { draft_id: draftId }
        }
      })

      if (response.error) {
        console.error('[草稿] 删除草稿失败:', response.error)
        return { error: response.error }
      }

      console.log('[草稿] 已删除服务端草稿, ID:', draftId)
      return { data: response.data }
    } catch (error) {
      console.error('[草稿] 删除草稿异常:', error)
      return { error: error.message }
    }
  }

  return {
    draft,
    hasDraft,
    loadDraft,
    saveDraft,
    clearDraft,
    startAutoSave,
    stopAutoSave,
    // 服务端草稿方法
    saveDraftToServer,
    updateDraftToServer,
    fetchDraftsFromServer,
    fetchDraftDetail,
    deleteDraftFromServer
  }
}
