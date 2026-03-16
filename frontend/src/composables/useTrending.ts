/**
 * 热门内容 Composable
 *
 * 核心特性：
 * 1. 封装热门内容数据获取逻辑
 * 2. 管理 loading、error、data 状态
 * 3. 实现缓存机制（5分钟缓存，避免频繁请求）
 * 4. 支持按社区筛选
 */

import { ref, computed, onMounted } from 'vue'
import { client } from '@/api/client'

// TypeScript 接口定义（基于后端 API 响应格式）
export interface HotPost {
  id: number
  title: string
  score: number
  hot_rank: number
  community_name: string
  author_username: string
  created_at: string
}

export interface HotCommunity {
  id: number
  name: string
  description: string
  member_count: number
  post_count: number
  hot_rank: number
}

export interface HotUser {
  id: number
  username: string
  nickname: string | null
  avatar: string | null
  karma: number
  post_count: number
  comment_count: number
  hot_rank: number
}

export interface TrendingData {
  hot_posts: HotPost[]
  hot_communities: HotCommunity[]
  hot_users: HotUser[]
}

export interface UseTrendingOptions {
  limit?: number          // 每类内容数量（5-20，默认10）
  communityId?: number    // 可选，筛选特定社区
  autoFetch?: boolean     // 是否自动获取（默认true）
  cacheTime?: number      // 缓存时间（毫秒，默认5分钟）
}

export function useTrending(options: UseTrendingOptions = {}) {
  const {
    limit = 10,
    communityId,
    autoFetch = true,
    cacheTime = 5 * 60 * 1000 // 默认5分钟
  } = options

  // 状态管理
  const data = ref<TrendingData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 生成缓存键
  const getCacheKey = () => {
    return `trending_data_${limit}_${communityId || 'all'}`
  }

  // 从缓存读取数据
  const getFromCache = (): TrendingData | null => {
    try {
      const cacheKey = getCacheKey()
      const cached = localStorage.getItem(cacheKey)
      if (!cached) return null

      const { data: cachedData, timestamp } = JSON.parse(cached)
      const now = Date.now()

      // 检查缓存是否过期
      if (now - timestamp > cacheTime) {
        localStorage.removeItem(cacheKey)
        return null
      }

      return cachedData as TrendingData
    } catch (e) {
      console.error('[useTrending] 读取缓存失败:', e)
      return null
    }
  }

  // 保存数据到缓存
  const saveToCache = (trendingData: TrendingData) => {
    try {
      const cacheKey = getCacheKey()
      const cacheData = {
        data: trendingData,
        timestamp: Date.now()
      }
      localStorage.setItem(cacheKey, JSON.stringify(cacheData))
    } catch (e) {
      console.error('[useTrending] 保存缓存失败:', e)
    }
  }

  // 清除缓存
  const clearCache = () => {
    try {
      const cacheKey = getCacheKey()
      localStorage.removeItem(cacheKey)
    } catch (e) {
      console.error('[useTrending] 清除缓存失败:', e)
    }
  }

  // 获取热门内容数据
  const fetchTrending = async () => {
    // 先检查缓存
    const cachedData = getFromCache()
    if (cachedData) {
      console.log('[useTrending] 使用缓存数据')
      data.value = cachedData
      return
    }

    loading.value = true
    error.value = null

    try {
      const response = await client.GET('/v1/sidebar' as any, {
        params: {
          query: {
            limit,
            community_id: communityId
          }
        }
      } as any)

      if (response.data) {
        const trendingData = response.data as any
        data.value = {
          hot_posts: trendingData.hot_posts || [],
          hot_communities: trendingData.hot_communities || [],
          hot_users: trendingData.hot_users || []
        }
        // 保存到缓存
        saveToCache(data.value)
        console.log('[useTrending] 数据加载成功:', {
          posts: data.value.hot_posts?.length || 0,
          communities: data.value.hot_communities?.length || 0,
          users: data.value.hot_users?.length || 0
        })
      } else if (response.error) {
        throw new Error(response.error.message || '获取热门内容失败')
      } else {
        throw new Error('未知错误')
      }
    } catch (e: any) {
      console.error('[useTrending] 获取数据失败:', e)
      error.value = e.message || '获取热门内容失败'

      // 降级策略：如果有缓存数据，即使过期也使用
      const cachedData = getFromCache()
      if (cachedData) {
        console.log('[useTrending] 请求失败，使用过期缓存数据')
        data.value = cachedData
      }
    } finally {
      loading.value = false
    }
  }

  // 强制刷新（忽略缓存）
  const refreshTrending = async () => {
    clearCache()
    await fetchTrending()
  }

  // 计算属性：便捷访问各类数据
  const hotPosts = computed(() => data.value?.hot_posts || [])
  const hotCommunities = computed(() => data.value?.hot_communities || [])
  const hotUsers = computed(() => data.value?.hot_users || [])

  // 自动获取
  if (autoFetch) {
    onMounted(() => {
      fetchTrending()
    })
  }

  return {
    // 状态
    data,
    loading,
    error,

    // 分类数据
    hotPosts,
    hotCommunities,
    hotUsers,

    // 方法
    fetchTrending,
    refreshTrending,
    clearCache
  }
}
