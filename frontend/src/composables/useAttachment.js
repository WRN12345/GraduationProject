/**
 * 附件访问 Composable
 */
import { ref, computed, watch, toValue } from 'vue'
import {
  getAttachmentUrl,
  batchGetAttachmentUrls,
  presignedUrlCache
} from '@/api/attachment'

/**
 * 单个附件 URL 管理
 * @param {number} attachmentId
 * @param {string} fallbackUrl
 */
export function useAttachment(attachmentId, fallbackUrl = null) {
  const url = ref(fallbackUrl)
  const loading = ref(false)
  const error = ref(null)

  const loadUrl = async () => {
    if (!attachmentId) {
      return
    }

    // 先检查缓存
    const cached = presignedUrlCache.get(attachmentId)
    if (cached) {
      url.value = cached
      return
    }

    loading.value = true
    error.value = null

    try {
      url.value = await getAttachmentUrl(attachmentId, fallbackUrl)
    } catch (err) {
      error.value = err
      console.error('[useAttachment] 加载失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 立即加载
  loadUrl()

  return {
    url,
    loading,
    error,
    reload: loadUrl
  }
}

/**
 * 批量附件 URL 管理
 * @param {Array<{id: number, file_url: string}>} attachments
 */
export function useAttachments(attachments) {
  const urls = ref({})
  const loading = ref(false)
  const error = ref(null)

  // 使用 toValue 支持 Ref 和普通数组
  const attachmentIds = computed(() => {
    const arr = toValue(attachments) || []
    return arr.map(a => a.id).filter(Boolean)
  })

  const fallbackUrls = computed(() => {
    const arr = toValue(attachments) || []
    return arr.reduce((acc, a) => {
      if (a.id) {
        acc[a.id] = a.file_url
      }
      return acc
    }, {})
  })

  const loadUrls = async () => {
    if (attachmentIds.value.length === 0) {
      return
    }

    loading.value = true
    error.value = null

    try {
      urls.value = await batchGetAttachmentUrls(
        attachmentIds.value,
        fallbackUrls.value
      )
    } catch (err) {
      error.value = err
      console.error('[useAttachments] 批量加载失败:', err)
    } finally {
      loading.value = false
    }
  }

  // 立即加载（如果已有数据）
  loadUrls()

  // 监听 attachmentIds 变化，自动重新加载
  watch(attachmentIds, (newIds, oldIds) => {
    // 只在从空变为有值，或 IDs 实际变化时重新加载
    const newIdsStr = JSON.stringify(newIds)
    const oldIdsStr = JSON.stringify(oldIds)
    if (newIds.length > 0 && newIdsStr !== oldIdsStr) {
      console.log('[useAttachments] attachmentIds 变化，重新加载:', newIds)
      loadUrls()
    }
  })

  return {
    urls,
    loading,
    error,
    reload: loadUrls
  }
}
