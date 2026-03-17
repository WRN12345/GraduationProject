/**
 * 搜索功能 Composable
 *
 * 核心特性：
 * 1. 封装搜索建议获取逻辑
 * 2. 封装各种搜索类型的获取逻辑
 * 3. 管理 loading、error、data 状态
 * 4. 支持防抖处理（避免频繁请求）
 * 5. 支持分页
 */

import { ref, computed, watch } from 'vue'
import { client } from '@/api/client'

// TypeScript 接口定义（基于后端 API 响应格式）
export interface SearchResultPost {
  id: number
  title: string
  content: string | null
  author: {
    id: number
    username: string
    nickname: string | null
    avatar: string | null
  }
  community: {
    id: number
    name: string
  } | null
  created_at: string
  upvotes: number
  downvotes: number
  comment_count: number
  headline?: string // 高亮后的内容
}

export interface SearchResultUser {
  id: number
  username: string
  nickname: string | null
  avatar: string | null
  karma: number
  post_count: number
  comment_count: number
}

export interface SearchResultComment {
  id: number
  content: string
  author: {
    id: number
    username: string
    nickname: string | null
    avatar: string | null
  }
  post: {
    id: number
    title: string
  }
  created_at: string
  upvotes: number
  downvotes: number
  headline?: string // 高亮后的内容
}

export interface SearchSuggestionData {
  posts: SearchResultPost[]
  users: SearchResultUser[]
  query: string
  totals: {
    posts: number
    users: number
  }
}

export interface SearchAllData {
  posts: SearchResultPost[]
  comments: SearchResultComment[]
  users: SearchResultUser[]
  total: number
  query: string
}

export interface SearchData {
  results: SearchResultPost[] | SearchResultUser[] | SearchResultComment[]
  total: number
  query: string
}

// 热搜内容接口定义
export interface HotPost {
  id: number
  title: string
  hot_rank: number
  community_name: string
  author_username: string
  created_at: string
  score?: number
}

export interface HotUser {
  id: number
  username: string
  nickname: string | null
  avatar: string | null
  karma: number
  post_count: number
  comment_count: number
}

export interface HotCommunity {
  id: number
  name: string
  description: string
  member_count: number
  post_count: number
}

export interface UseSearchOptions {
  debounceTime?: number  // 防抖时间（毫秒，默认300）
}

export function useSearch(options: UseSearchOptions = {}) {
  const {
    debounceTime = 300
  } = options

  // 搜索建议状态
  const suggestions = ref<SearchSuggestionData | null>(null)
  const suggestionsLoading = ref(false)
  const suggestionsError = ref<string | null>(null)

  // 搜索结果状态
  const searchResults = ref<SearchAllData | null>(null)
  const searchLoading = ref(false)
  const searchError = ref<string | null>(null)

  // 分页状态
  const currentTab = ref<'all' | 'posts' | 'users' | 'comments'>('posts')
  const currentPage = ref(0)
  const pageSize = 20
  const hasMore = ref(true)

  // 当前搜索查询
  const currentQuery = ref('')

  // 热搜状态
  const hotPosts = ref<HotPost[]>([])
  const hotUsers = ref<HotUser[]>([])
  const hotCommunities = ref<HotCommunity[]>([])
  const hotLoading = ref(false)
  const hotError = ref<string | null>(null)
  const hotLoaded = ref(false) // 是否已加载过热搜（避免重复请求）

  // 防抖函数
  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  const debounce = (fn: Function, delay: number) => {
    return (...args: any[]) => {
      if (debounceTimer) {
        clearTimeout(debounceTimer)
      }
      debounceTimer = setTimeout(() => {
        fn(...args)
      }, delay)
    }
  }

  // 获取搜索建议
  const fetchSuggestions = async (query: string) => {
    if (!query || query.trim().length < 1) {
      suggestions.value = null
      return
    }

    suggestionsLoading.value = true
    suggestionsError.value = null

    try {
      const response = await client.GET('/v1/search' as any, {
        params: {
          query: { q: query.trim() }
        }
      } as any)

      if (response.data) {
        suggestions.value = response.data as SearchSuggestionData
        console.log('[useSearch] 搜索建议加载成功:', {
          posts: suggestions.value.posts?.length || 0,
          users: suggestions.value.users?.length || 0
        })
      } else if (response.error) {
        throw new Error(response.error.message || '获取搜索建议失败')
      }
    } catch (e: any) {
      console.error('[useSearch] 获取搜索建议失败:', e)
      suggestionsError.value = e.message || '获取搜索建议失败'
      suggestions.value = null
    } finally {
      suggestionsLoading.value = false
    }
  }

  // 防抖版本的搜索建议
  const debouncedFetchSuggestions = debounce(fetchSuggestions, debounceTime)

  // 统一搜索
  const searchAll = async (query: string, reset = true) => {
    if (!query || query.trim().length < 1) {
      return
    }

    if (reset) {
      currentPage.value = 0
      hasMore.value = true
      searchResults.value = null
    }

    if (!hasMore.value && !reset) {
      return
    }

    searchLoading.value = true
    searchError.value = null
    currentQuery.value = query.trim()

    try {
      const response = await client.GET('/v1/search/all' as any, {
        params: {
          query: {
            q: currentQuery.value,
            skip: currentPage.value * pageSize,
            limit: pageSize
          }
        }
      } as any)

      if (response.data) {
        const data = response.data as SearchAllData

        if (reset) {
          searchResults.value = data
        } else {
          // 追加数据
          if (searchResults.value) {
            searchResults.value.posts.push(...data.posts)
            searchResults.value.comments.push(...data.comments)
            searchResults.value.users.push(...data.users)
            searchResults.value.total = data.total
          } else {
            searchResults.value = data
          }
        }

        hasMore.value = (data.posts?.length || 0) +
                       (data.comments?.length || 0) +
                       (data.users?.length || 0) >= pageSize
        currentPage.value++

        console.log('[useSearch] 统一搜索成功:', {
          posts: data.posts?.length || 0,
          comments: data.comments?.length || 0,
          users: data.users?.length || 0,
          total: data.total
        })
      } else if (response.error) {
        throw new Error(response.error.message || '搜索失败')
      }
    } catch (e: any) {
      console.error('[useSearch] 统一搜索失败:', e)
      searchError.value = e.message || '搜索失败'
    } finally {
      searchLoading.value = false
    }
  }

  // 搜索帖子
  const searchPosts = async (query: string, reset = true) => {
    if (!query || query.trim().length < 1) {
      return
    }

    if (reset) {
      currentPage.value = 0
      hasMore.value = true
    }

    if (!hasMore.value && !reset) {
      return
    }

    searchLoading.value = true
    searchError.value = null
    currentQuery.value = query.trim()

    try {
      const response = await client.GET('/v1/search/posts' as any, {
        params: {
          query: {
            q: currentQuery.value,
            skip: currentPage.value * pageSize,
            limit: pageSize
          }
        }
      } as any)

      if (response.data) {
        const data = response.data as SearchData
        const posts = data.results as SearchResultPost[]

        if (reset) {
          searchResults.value = {
            posts: posts,
            comments: [],
            users: [],
            total: data.total,
            query: data.query
          }
        } else {
          if (searchResults.value) {
            searchResults.value.posts.push(...posts)
          } else {
            searchResults.value = {
              posts: posts,
              comments: [],
              users: [],
              total: data.total,
              query: data.query
            }
          }
        }

        hasMore.value = posts.length >= pageSize
        currentPage.value++

        console.log('[useSearch] 帖子搜索成功:', {
          count: posts.length,
          total: data.total
        })
      } else if (response.error) {
        throw new Error(response.error.message || '搜索帖子失败')
      }
    } catch (e: any) {
      console.error('[useSearch] 帖子搜索失败:', e)
      searchError.value = e.message || '搜索帖子失败'
    } finally {
      searchLoading.value = false
    }
  }

  // 搜索用户
  const searchUsers = async (query: string, reset = true) => {
    if (!query || query.trim().length < 1) {
      return
    }

    if (reset) {
      currentPage.value = 0
      hasMore.value = true
    }

    if (!hasMore.value && !reset) {
      return
    }

    searchLoading.value = true
    searchError.value = null
    currentQuery.value = query.trim()

    try {
      const response = await client.GET('/v1/search/users' as any, {
        params: {
          query: {
            q: currentQuery.value,
            skip: currentPage.value * pageSize,
            limit: pageSize
          }
        }
      } as any)

      if (response.data) {
        const data = response.data as SearchData
        const users = data.results as SearchResultUser[]

        if (reset) {
          searchResults.value = {
            posts: [],
            comments: [],
            users: users,
            total: data.total,
            query: data.query
          }
        } else {
          if (searchResults.value) {
            searchResults.value.users.push(...users)
          } else {
            searchResults.value = {
              posts: [],
              comments: [],
              users: users,
              total: data.total,
              query: data.query
            }
          }
        }

        hasMore.value = users.length >= pageSize
        currentPage.value++

        console.log('[useSearch] 用户搜索成功:', {
          count: users.length,
          total: data.total
        })
      } else if (response.error) {
        throw new Error(response.error.message || '搜索用户失败')
      }
    } catch (e: any) {
      console.error('[useSearch] 用户搜索失败:', e)
      searchError.value = e.message || '搜索用户失败'
    } finally {
      searchLoading.value = false
    }
  }

  // 搜索评论
  const searchComments = async (query: string, reset = true) => {
    if (!query || query.trim().length < 1) {
      return
    }

    if (reset) {
      currentPage.value = 0
      hasMore.value = true
    }

    if (!hasMore.value && !reset) {
      return
    }

    searchLoading.value = true
    searchError.value = null
    currentQuery.value = query.trim()

    try {
      const response = await client.GET('/v1/search/comments' as any, {
        params: {
          query: {
            q: currentQuery.value,
            skip: currentPage.value * pageSize,
            limit: pageSize
          }
        }
      } as any)

      if (response.data) {
        const data = response.data as SearchData
        const comments = data.results as SearchResultComment[]

        if (reset) {
          searchResults.value = {
            posts: [],
            comments: comments,
            users: [],
            total: data.total,
            query: data.query
          }
        } else {
          if (searchResults.value) {
            searchResults.value.comments.push(...comments)
          } else {
            searchResults.value = {
              posts: [],
              comments: comments,
              users: [],
              total: data.total,
              query: data.query
            }
          }
        }

        hasMore.value = comments.length >= pageSize
        currentPage.value++

        console.log('[useSearch] 评论搜索成功:', {
          count: comments.length,
          total: data.total
        })
      } else if (response.error) {
        throw new Error(response.error.message || '搜索评论失败')
      }
    } catch (e: any) {
      console.error('[useSearch] 评论搜索失败:', e)
      searchError.value = e.message || '搜索评论失败'
    } finally {
      searchLoading.value = false
    }
  }

  // 根据当前标签执行搜索
  const searchByTab = async (query: string, tab: 'posts' | 'users' | 'comments', reset = true) => {
    currentTab.value = tab

    switch (tab) {
      case 'posts':
        await searchPosts(query, reset)
        break
      case 'users':
        await searchUsers(query, reset)
        break
      case 'comments':
        await searchComments(query, reset)
        break
    }
  }

  // 加载更多
  const loadMore = () => {
    if (!currentQuery.value || !hasMore.value || searchLoading.value) {
      return
    }

    switch (currentTab.value) {
      case 'posts':
        searchPosts(currentQuery.value, false)
        break
      case 'users':
        searchUsers(currentQuery.value, false)
        break
      case 'comments':
        searchComments(currentQuery.value, false)
        break
    }
  }

  // 清除搜索建议
  const clearSuggestions = () => {
    suggestions.value = null
    suggestionsError.value = null
  }

  // 获取热搜内容
  const fetchHotContent = async (limit = 5) => {
    // 如果已经加载过，直接返回（避免重复请求）
    if (hotLoaded.value) {
      return
    }

    hotLoading.value = true
    hotError.value = null

    try {
      const response = await client.GET('/v1/sidebar' as any, {
        params: {
          query: { limit }
        }
      } as any)

      if (response.data) {
        const data = response.data as any
        hotPosts.value = data.hot_posts || []
        hotUsers.value = data.hot_users || []
        hotCommunities.value = data.hot_communities || []
        hotLoaded.value = true

        console.log('[useSearch] 热搜内容加载成功:', {
          posts: hotPosts.value.length,
          users: hotUsers.value.length,
          communities: hotCommunities.value.length
        })
      } else if (response.error) {
        throw new Error(response.error.message || '获取热搜内容失败')
      }
    } catch (e: any) {
      console.error('[useSearch] 获取热搜内容失败:', e)
      hotError.value = e.message || '获取热搜内容失败'
    } finally {
      hotLoading.value = false
    }
  }

  // 清除热搜内容
  const clearHotContent = () => {
    hotPosts.value = []
    hotUsers.value = []
    hotCommunities.value = []
    hotError.value = null
    // 不重置 hotLoaded，保持缓存状态
  }

  // 计算属性：便捷访问搜索建议
  const suggestionPosts = computed(() => suggestions.value?.posts || [])
  const suggestionUsers = computed(() => suggestions.value?.users || [])

  // 计算属性：便捷访问搜索结果
  const resultPosts = computed(() => searchResults.value?.posts || [])
  const resultUsers = computed(() => searchResults.value?.users || [])
  const resultComments = computed(() => searchResults.value?.comments || [])
  const totalResults = computed(() => searchResults.value?.total || 0)

  return {
    // 搜索建议
    suggestions,
    suggestionPosts,
    suggestionUsers,
    suggestionsLoading,
    suggestionsError,
    fetchSuggestions,
    debouncedFetchSuggestions,
    clearSuggestions,

    // 搜索结果
    searchResults,
    resultPosts,
    resultUsers,
    resultComments,
    totalResults,
    searchLoading,
    searchError,
    searchPosts,
    searchUsers,
    searchComments,
    searchByTab,
    loadMore,

    // 热搜内容
    hotPosts,
    hotUsers,
    hotCommunities,
    hotLoading,
    hotError,
    hotLoaded,
    fetchHotContent,
    clearHotContent,

    // 状态
    currentTab,
    currentQuery,
    currentPage,
    hasMore
  }
}
