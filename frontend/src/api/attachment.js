/**
 * 附件访问 API
 */
import { client } from './client'

/**
 * 获取单个附件的 presigned URL
 * @param {number} attachmentId - 附件 ID
 * @returns {Promise<{presigned_url: string, expires_in: number}>}
 */
export async function getPresignedUrl(attachmentId) {
  const response = await client.GET('/v1/attachments/{attachment_id}/presigned-url', {
    params: {
      path: { attachment_id: attachmentId }
    }
  })

  if (response.data) {
    return response.data
  }

  throw new Error('获取临时链接失败')
}

/**
 * 批量获取附件的 presigned URLs
 * @param {number[]} attachmentIds - 附件 ID 列表
 * @returns {Promise<{[key: number]: string}>} - {attachment_id: presigned_url}
 */
export async function batchGetPresignedUrls(attachmentIds) {
  if (!attachmentIds || attachmentIds.length === 0) {
    return {}
  }

  const response = await client.POST('/v1/attachments/batch-presigned-urls', {
    body: {
      attachment_ids: attachmentIds
    }
  })

  if (response.data) {
    return response.data.urls
  }

  throw new Error('批量获取临时链接失败')
}

/**
 * presigned URL 缓存管理器
 */
class PresignedUrlCache {
  constructor() {
    this.cache = new Map()
    this.ttl = 23 * 60 * 60 * 1000 // 23小时（毫秒）
  }

  /**
   * 获取缓存的 presigned URL
   * @param {number} attachmentId
   * @returns {string|null}
   */
  get(attachmentId) {
    const cached = this.cache.get(attachmentId)
    if (!cached) {
      return null
    }

    // 检查是否过期
    if (Date.now() - cached.timestamp > this.ttl) {
      this.cache.delete(attachmentId)
      return null
    }

    return cached.url
  }

  /**
   * 设置缓存
   * @param {number} attachmentId
   * @param {string} url
   */
  set(attachmentId, url) {
    this.cache.set(attachmentId, {
      url,
      timestamp: Date.now()
    })
  }

  /**
   * 批量设置缓存
   * @param {{[key: number]: string}} urls
   */
  setBatch(urls) {
    Object.entries(urls).forEach(([id, url]) => {
      this.set(parseInt(id), url)
    })
  }

  /**
   * 清除缓存
   * @param {number} attachmentId
   */
  clear(attachmentId) {
    this.cache.delete(attachmentId)
  }

  /**
   * 清空所有缓存
   */
  clearAll() {
    this.cache.clear()
  }
}

// 导出全局缓存实例
export const presignedUrlCache = new PresignedUrlCache()

/**
 * 获取附件 URL（带缓存）
 * @param {number} attachmentId
 * @param {string} fallbackUrl - 降级使用的原始 URL
 * @returns {Promise<string>}
 */
export async function getAttachmentUrl(attachmentId, fallbackUrl = null) {
  // 先检查本地缓存
  const cached = presignedUrlCache.get(attachmentId)
  if (cached) {
    return cached
  }

  try {
    // 请求新的 presigned URL
    const result = await getPresignedUrl(attachmentId)
    presignedUrlCache.set(attachmentId, result.presigned_url)
    return result.presigned_url
  } catch (error) {
    console.error('[Attachment] 获取 presigned URL 失败:', error)
    // 降级返回原始 URL
    return fallbackUrl
  }
}

/**
 * 批量获取附件 URL（带缓存）
 * @param {number[]} attachmentIds
 * @param {{[key: number]: string}} fallbackUrls - 降级使用的原始 URLs
 * @returns {Promise<{[key: number]: string}>}
 */
export async function batchGetAttachmentUrls(attachmentIds, fallbackUrls = {}) {
  const result = {}
  const missedIds = []

  // 先从本地缓存获取
  attachmentIds.forEach(id => {
    const cached = presignedUrlCache.get(id)
    if (cached) {
      result[id] = cached
    } else {
      missedIds.push(id)
    }
  })

  // 批量请求未命中的
  if (missedIds.length > 0) {
    try {
      const urls = await batchGetPresignedUrls(missedIds)
      presignedUrlCache.setBatch(urls)
      Object.assign(result, urls)
    } catch (error) {
      console.error('[Attachment] 批量获取 presigned URLs 失败:', error)
      // 降级使用原始 URLs
      missedIds.forEach(id => {
        if (fallbackUrls[id]) {
          result[id] = fallbackUrls[id]
        }
      })
    }
  }

  return result
}
