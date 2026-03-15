/**
 * 收藏逻辑 Composable
 *
 * 核心特性：
 * 1. 乐观更新（Optimistic UI）- 点击立即更新 UI
 * 2. 立即请求 - 移除防抖，提供及时反馈
 * 3. 回滚机制 - 失败时静默回滚
 * 4. 操作保护 - 防止重复点击
 */

import { ref, computed } from 'vue'
import { client } from '@/api/client'
import { ElMessage } from 'element-plus'

export interface UseBookmarkOptions {
  postId: number
  initialBookmarked?: boolean
  initialCount?: number
}

export function useBookmark(options: UseBookmarkOptions) {
  const {
    postId,
    initialBookmarked = false,
    initialCount = 0
  } = options

  // 本地状态（使用 internal 前缀避免返回时的命名冲突）
  const internalBookmarked = ref(initialBookmarked)
  const internalCount = ref(Math.max(0, initialCount))
  const loading = ref(false)

  // 操作保护标志
  const isOperating = ref(false)

  // 回滚数据
  const rollbackData = ref<{ bookmarked: boolean; count: number } | null>(null)

  /**
   * 切换收藏状态
   * 乐观更新 + 立即请求
   */
  const toggleBookmark = async () => {
    // 防止重复操作
    if (isOperating.value || loading.value) {
      console.log('[useBookmark] 操作正在进行中，忽略点击')
      return
    }

    const newState = !internalBookmarked.value
    const previousState = internalBookmarked.value
    const previousCount = internalCount.value

    console.log('[useBookmark] 切换收藏状态:', { previousState, newState, postId })

    // 1. 保存回滚数据
    rollbackData.value = {
      bookmarked: previousState,
      count: previousCount
    }

    // 2. 立即更新 UI（乐观更新）
    internalBookmarked.value = newState
    internalCount.value = Math.max(0, internalCount.value + (newState ? 1 : -1))

    // 3. 标记操作开始
    isOperating.value = true

    try {
      // 4. 立即发送请求
      await sendToBackend(newState, previousState)
    } finally {
      // 5. 操作完成
      isOperating.value = false
    }
  }

  /**
   * 发送请求到后端
   */
  const sendToBackend = async (
    finalState: boolean,
    previousBookmarked: boolean
  ) => {
    loading.value = true
    try {
      console.log('[useBookmark] 发送收藏请求:', { postId, finalState })

      if (finalState) {
        // 添加收藏
        const response = await client.POST('/v1/bookmarks', {
          body: { post_id: postId }
        })

        console.log('[useBookmark] 收藏响应:', response)

        if (response.error) {
          console.error('[useBookmark] 收藏失败:', response.error)
          throw new Error(response.error.message || '收藏失败')
        }
      } else {
        // 取消收藏
        const response = await client.DELETE('/v1/bookmarks/{post_id}', {
          params: { path: { post_id: postId } }
        })

        console.log('[useBookmark] 取消收藏响应:', response)

        if (response.error) {
          console.error('[useBookmark] 取消收藏失败:', response.error)
          throw new Error(response.error.message || '取消收藏失败')
        }
      }

      console.log('[useBookmark] 收藏操作成功')
    } catch (error: any) {
      // 失败时回滚
      if (rollbackData.value) {
        internalBookmarked.value = rollbackData.value.bookmarked
        internalCount.value = Math.max(0, rollbackData.value.count)
      }
      console.error('收藏操作失败:', error)
      ElMessage.warning({
        message: error.message || '操作失败，请重试',
        duration: 2000
      })
    } finally {
      loading.value = false
    }
  }

  /**
   * 刷新收藏状态
   */
  const refreshBookmarkStatus = async () => {
    if (loading.value || isOperating.value) return

    loading.value = true
    try {
      const response = await client.GET('/v1/bookmarks/check/{post_id}', {
        params: { path: { post_id: postId } }
      })

      if (response.data) {
        internalBookmarked.value = response.data.bookmarked
      }

      // 同时获取收藏数
      const countResponse = await client.GET('/v1/posts/{post_id}/bookmark-count', {
        params: { path: { post_id: postId } }
      })

      if (countResponse.data) {
        internalCount.value = Math.max(0, countResponse.data.bookmark_count)
      }
    } catch (error) {
      console.error('刷新收藏状态失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 返回响应式状态和方法
  return {
    // 状态（使用 computed 返回，确保响应式）
    bookmarked: computed(() => internalBookmarked.value),
    count: computed(() => Math.max(0, internalCount.value)),
    loading,
    isOperating,
    // 方法
    toggleBookmark,
    refreshBookmarkStatus
  }
}
