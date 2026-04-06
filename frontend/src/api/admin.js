/**
 * 超级管理员 API 接口
 * 管理员接口不在 OpenAPI schema 中，使用原生 fetch 调用
 */

const BASE_URL = '/api/v1/admin'

/**
 * 获取认证请求头
 */
function getAuthHeaders() {
  const headers = {
    'Content-Type': 'application/json'
  }
  try {
    const tokenStr = localStorage.getItem('token')
    if (tokenStr) {
      const token = JSON.parse(tokenStr)
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }
  } catch (e) {
    console.error('[Admin API] 解析 token 失败:', e)
  }
  return headers
}

/**
 * 通用请求方法
 */
async function request(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options.headers
    }
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '请求失败' }))
    throw new Error(error.detail || `请求失败: ${response.status}`)
  }

  return response.json()
}

// ==================== 控制面板 ====================

/**
 * 获取控制面板统计数据
 */
export function getDashboardStats() {
  return request(`${BASE_URL}/dashboard`)
}

// ==================== 用户管理 ====================

/**
 * 获取所有用户列表
 */
export function getUsers(params = {}) {
  const query = new URLSearchParams()
  if (params.page) query.set('page', params.page)
  if (params.page_size) query.set('page_size', params.page_size)
  if (params.is_active !== undefined && params.is_active !== null) query.set('is_active', params.is_active)
  if (params.is_superuser !== undefined && params.is_superuser !== null) query.set('is_superuser', params.is_superuser)
  if (params.search) query.set('search', params.search)
  return request(`${BASE_URL}/users?${query.toString()}`)
}

/**
 * 获取用户详情
 */
export function getUserDetail(userId) {
  return request(`${BASE_URL}/users/${userId}`)
}

/**
 * 冻结用户
 */
export function banUser(userId, reason = null) {
  return request(`${BASE_URL}/users/${userId}/ban`, {
    method: 'POST',
    body: JSON.stringify({ reason })
  })
}

/**
 * 解冻用户
 */
export function unbanUser(userId, reason = null) {
  return request(`${BASE_URL}/users/${userId}/unban`, {
    method: 'POST',
    body: JSON.stringify({ reason })
  })
}

// ==================== 帖子管理 ====================

/**
 * 获取所有帖子列表
 */
export function getPosts(params = {}) {
  const query = new URLSearchParams()
  if (params.page) query.set('page', params.page)
  if (params.page_size) query.set('page_size', params.page_size)
  if (params.include_deleted) query.set('include_deleted', 'true')
  if (params.search) query.set('search', params.search)
  return request(`${BASE_URL}/posts?${query.toString()}`)
}

/**
 * 管理员获取帖子详情
 */
export function getPostDetail(postId) {
  return request(`${BASE_URL}/posts/${postId}`)
}

/**
 * 管理员软删除帖子
 */
export function deletePost(postId, reason = null) {
  return request(`${BASE_URL}/posts/${postId}`, {
    method: 'DELETE',
    body: JSON.stringify({ reason })
  })
}

/**
 * 管理员恢复帖子
 */
export function restorePost(postId, reason = null) {
  return request(`${BASE_URL}/posts/${postId}/restore`, {
    method: 'POST',
    body: JSON.stringify({ reason })
  })
}

/**
 * 管理员硬删除帖子
 */
export function hardDeletePost(postId, reason = null) {
  return request(`${BASE_URL}/posts/${postId}/hard`, {
    method: 'DELETE',
    body: JSON.stringify({ reason })
  })
}

// ==================== 评论管理 ====================

/**
 * 获取所有评论列表
 */
export function getComments(params = {}) {
  const query = new URLSearchParams()
  if (params.page) query.set('page', params.page)
  if (params.page_size) query.set('page_size', params.page_size)
  if (params.include_deleted) query.set('include_deleted', 'true')
  if (params.search) query.set('search', params.search)
  return request(`${BASE_URL}/comments?${query.toString()}`)
}

/**
 * 管理员软删除评论
 */
export function deleteComment(commentId, reason = null) {
  return request(`${BASE_URL}/comments/${commentId}`, {
    method: 'DELETE',
    body: JSON.stringify({ reason })
  })
}

/**
 * 管理员恢复评论
 */
export function restoreComment(commentId, reason = null) {
  return request(`${BASE_URL}/comments/${commentId}/restore`, {
    method: 'POST',
    body: JSON.stringify({ reason })
  })
}

/**
 * 管理员硬删除评论
 */
export function hardDeleteComment(commentId, reason = null) {
  return request(`${BASE_URL}/comments/${commentId}/hard`, {
    method: 'DELETE',
    body: JSON.stringify({ reason })
  })
}

// ==================== 审计日志 ====================

/**
 * 获取审计日志列表
 */
export function getAuditLogs(params = {}) {
  const query = new URLSearchParams()
  if (params.page) query.set('page', params.page)
  if (params.page_size) query.set('page_size', params.page_size)
  if (params.admin_id) query.set('admin_id', params.admin_id)
  if (params.action_type) query.set('action_type', params.action_type)
  if (params.target_type) query.set('target_type', params.target_type)
  return request(`${BASE_URL}/audit-logs?${query.toString()}`)
}

// ==================== 图表数据 ====================

/**
 * 获取操作类型统计（用于图表）
 */
export function getActionStats() {
  return request(`${BASE_URL}/stats/action-stats`)
}

/**
 * 获取操作趋势（按天分组）
 */
export function getTrend(days = 30) {
  return request(`${BASE_URL}/stats/trend?days=${days}`)
}
