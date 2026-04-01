import { defineStore } from 'pinia'
import { client } from '@/api/client'

export const usePostListStore = defineStore('postList', {
  state: () => ({
    posts: [],
    currentPage: 0,
    pageSize: 20,
    hasMore: true,
    loading: false,
    error: null,
    scrollPosition: 0,
    lastLoadedAt: null // 用于判断是否需要刷新
  }),

  getters: {
    // 获取帖子列表
    getPosts: (state) => state.posts,
    
    // 是否还有更多数据
    hasMoreData: (state) => state.hasMore,
    
    // 是否正在加载
    isLoading: (state) => state.loading,
    
    // 获取当前页码
    getCurrentPage: (state) => state.currentPage,
    
    // 获取滚动位置
    getScrollPosition: (state) => state.scrollPosition
  },

  actions: {
    // 加载帖子列表
    async loadPosts(reset = false) {
      if (this.loading) return
      if (!this.hasMore && !reset) return

      // 如果是重置，清空数据
      if (reset) {
        this.currentPage = 0
        this.posts = []
        this.hasMore = true
        this.error = null
      }

      this.loading = true
      this.error = null

      try {
        const response = await client.GET('/v1/posts', {
          params: {
            query: {
              skip: this.currentPage * this.pageSize,
              limit: this.pageSize
            }
          }
        })

        if (response.data) {
          const newPosts = response.data.items || response.data
          
          if (reset) {
            this.posts = newPosts
          } else {
            // 避免重复添加相同的帖子
            const existingIds = new Set(this.posts.map(p => p.id))
            const uniquePosts = newPosts.filter(p => !existingIds.has(p.id))
            this.posts = [...this.posts, ...uniquePosts]
          }
          
          this.hasMore = response.data.has_more ?? (newPosts.length >= this.pageSize)
          this.currentPage++
          this.lastLoadedAt = Date.now()
        }
      } catch (err) {
        console.error('[PostList Store] 加载失败:', err)
        this.error = '加载失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },

    // 加载更多帖子
    async loadMore() {
      await this.loadPosts(false)
    },

    // 刷新帖子列表
    async refresh() {
      await this.loadPosts(true)
    },

    // 保存滚动位置
    saveScrollPosition(position) {
      this.scrollPosition = position
    },

    // 检查是否需要刷新（超过5分钟未刷新）
    needsRefresh() {
      if (!this.lastLoadedAt) return true
      const fiveMinutes = 5 * 60 * 1000
      return Date.now() - this.lastLoadedAt > fiveMinutes
    },

    // 更新单个帖子的投票状态
    updateVote(postId, voteState) {
      const post = this.posts.find(p => p.id === postId)
      if (post) {
        const oldVote = post.user_vote || 0
        
        // 更新用户投票
        post.user_vote = voteState.upvote ? 1 : (voteState.downvote ? -1 : 0)
        
        // 更新投票计数
        if (oldVote === 1 && post.user_vote !== 1) {
          post.upvotes = (post.upvotes || 0) - 1
        } else if (oldVote !== 1 && post.user_vote === 1) {
          post.upvotes = (post.upvotes || 0) + 1
        }
        
        if (oldVote === -1 && post.user_vote !== -1) {
          post.downvotes = (post.downvotes || 0) - 1
        } else if (oldVote !== -1 && post.user_vote === -1) {
          post.downvotes = (post.downvotes || 0) + 1
        }
      }
    },

    // 更新单个帖子的收藏状态
    updateBookmark(postId, bookmarked, count) {
      const post = this.posts.find(p => p.id === postId)
      if (post) {
        post.bookmarked = bookmarked
        if (count !== undefined) {
          post.bookmark_count = count
        }
      }
    },

    // 更新帖子评论数
    updateCommentCount(postId, count) {
      const post = this.posts.find(p => p.id === postId)
      if (post) {
        post.comment_count = count
      }
    }
  }
})