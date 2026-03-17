<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowBigUp, Calendar, MessageCircle, FileText, ThumbsUp, ThumbsDown } from 'lucide-vue-next'
import { client } from '@/api/client'
import { marked } from 'marked'
import VoteButtons from '@/components/VoteButtons.vue'
import BookmarkButton from '@/components/BookmarkButton.vue'
import UserTabs from '@/components/user/UserTabs.vue'

const route = useRoute()
const router = useRouter()

// 从路由参数获取用户名
const username = computed(() => route.params.username)

// 用户信息状态
const userInfo = ref(null)
const userLoading = ref(false)
const userError = ref(null)

// 当前活动标签
const activeTab = ref('posts')

// 帖子状态
const posts = ref([])
const postsLoading = ref(false)
const postsError = ref(null)

// 评论状态
const comments = ref([])
const commentsLoading = ref(false)
const commentsError = ref(null)

// 点赞状态
const upvoted = ref([])
const upvotedLoading = ref(false)
const upvotedError = ref(null)

// 点踩状态
const downvoted = ref([])
const downvotedLoading = ref(false)
const downvotedError = ref(null)

// 分页
const currentPage = ref(0)
const pageSize = 20
const hasMore = ref(true)

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

// 获取头像文字（首字母）
const getAvatarText = (user) => {
  const name = user?.username || 'U'
  return name.charAt(0).toUpperCase()
}

// 头像加载失败处理
const handleAvatarError = (event) => {
  event.target.style.display = 'none'
}

// 格式化时间
const formatTime = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  const now = new Date()
  const diff = (now - date) / 1000

  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  if (diff < 604800) return `${Math.floor(diff / 86400)} 天前`

  return date.toLocaleDateString('zh-CN')
}

// 格式化加入时间
const formatJoinTime = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return `加入于 ${date.getFullYear()}年${date.getMonth() + 1}月`
}

// 渲染 Markdown（预览，只显示前200个字符）
const renderPreview = (content) => {
  if (!content) return ''
  try {
    const html = marked(content)
    const text = html.replace(/<[^>]*>/g, '')
    return text.length > 200 ? text.substring(0, 200) + '...' : text
  } catch (error) {
    console.error('[UserDetail] Markdown 渲染错误:', error)
    return content?.substring(0, 200) || ''
  }
}

// 获取用户信息
const fetchUserInfo = async () => {
  if (!username.value) return

  userLoading.value = true
  userError.value = null

  try {
    const response = await client.GET('/v1/users/{username}', {
      params: {
        path: { username: username.value }
      }
    })

    if (response.data) {
      userInfo.value = response.data
      console.log('[UserDetail] 用户信息加载成功:', userInfo.value)
    } else if (response.error) {
      throw new Error(response.error.message || '获取用户信息失败')
    }
  } catch (e) {
    console.error('[UserDetail] 获取用户信息失败:', e)
    userError.value = e.message || '获取用户信息失败'
  } finally {
    userLoading.value = false
  }
}

// 获取用户帖子
const fetchUserPosts = async (reset = false) => {
  if (!username.value) return
  if (postsLoading.value) return

  if (reset) {
    currentPage.value = 0
    posts.value = []
    hasMore.value = true
  }

  if (!hasMore.value) return

  postsLoading.value = true
  postsError.value = null

  try {
    const response = await client.GET('/v1/users/{username}/posts', {
      params: {
        path: { username: username.value },
        query: {
          skip: currentPage.value * pageSize,
          limit: pageSize
        }
      }
    })

    if (response.data) {
      const data = response.data
      const newPosts = data.items || data || []

      console.log('[UserDetail] 用户帖子加载成功:', newPosts.length)

      posts.value = reset ? newPosts : [...posts.value, ...newPosts]
      hasMore.value = newPosts.length >= pageSize
      currentPage.value++
    } else if (response.error) {
      throw new Error(response.error.message || '获取用户帖子失败')
    }
  } catch (e) {
    console.error('[UserDetail] 获取用户帖子失败:', e)
    postsError.value = e.message || '获取用户帖子失败'
  } finally {
    postsLoading.value = false
  }
}

// 获取用户评论
const fetchUserComments = async (reset = false) => {
  if (!username.value) return
  if (commentsLoading.value) return

  if (reset) {
    currentPage.value = 0
    comments.value = []
    hasMore.value = true
  }

  if (!hasMore.value) return

  commentsLoading.value = true
  commentsError.value = null

  try {
    const response = await client.GET('/v1/users/{username}/comments', {
      params: {
        path: { username: username.value },
        query: {
          skip: currentPage.value * pageSize,
          limit: pageSize
        }
      }
    })

    if (response.data) {
      const data = response.data
      const newComments = data.items || data || []

      console.log('[UserDetail] 用户评论加载成功:', newComments.length)

      comments.value = reset ? newComments : [...comments.value, ...newComments]
      hasMore.value = newComments.length >= pageSize
      currentPage.value++
    } else if (response.error) {
      throw new Error(response.error.message || '获取用户评论失败')
    }
  } catch (e) {
    console.error('[UserDetail] 获取用户评论失败:', e)
    commentsError.value = e.message || '获取用户评论失败'
  } finally {
    commentsLoading.value = false
  }
}

// 获取用户点赞的内容
const fetchUserUpvoted = async (reset = false) => {
  if (!username.value) return
  if (upvotedLoading.value) return

  if (reset) {
    currentPage.value = 0
    upvoted.value = []
    hasMore.value = true
  }

  if (!hasMore.value) return

  upvotedLoading.value = true
  upvotedError.value = null

  try {
    const response = await client.GET('/v1/users/{username}/upvoted', {
      params: {
        path: { username: username.value },
        query: {
          skip: currentPage.value * pageSize,
          limit: pageSize
        }
      }
    })

    if (response.data) {
      const data = response.data
      const newItems = data.items || data || []

      console.log('[UserDetail] 用户点赞加载成功:', newItems.length)

      upvoted.value = reset ? newItems : [...upvoted.value, ...newItems]
      hasMore.value = newItems.length >= pageSize
      currentPage.value++
    } else if (response.error) {
      throw new Error(response.error.message || '获取用户点赞失败')
    }
  } catch (e) {
    console.error('[UserDetail] 获取用户点赞失败:', e)
    upvotedError.value = e.message || '获取用户点赞失败'
  } finally {
    upvotedLoading.value = false
  }
}

// 获取用户点踩的内容
const fetchUserDownvoted = async (reset = false) => {
  if (!username.value) return
  if (downvotedLoading.value) return

  if (reset) {
    currentPage.value = 0
    downvoted.value = []
    hasMore.value = true
  }

  if (!hasMore.value) return

  downvotedLoading.value = true
  downvotedError.value = null

  try {
    const response = await client.GET('/v1/users/{username}/downvoted', {
      params: {
        path: { username: username.value },
        query: {
          skip: currentPage.value * pageSize,
          limit: pageSize
        }
      }
    })

    if (response.data) {
      const data = response.data
      const newItems = data.items || data || []

      console.log('[UserDetail] 用户点踩加载成功:', newItems.length)

      downvoted.value = reset ? newItems : [...downvoted.value, ...newItems]
      hasMore.value = newItems.length >= pageSize
      currentPage.value++
    } else if (response.error) {
      throw new Error(response.error.message || '获取用户点踩失败')
    }
  } catch (e) {
    console.error('[UserDetail] 获取用户点踩失败:', e)
    downvotedError.value = e.message || '获取用户点踩失败'
  } finally {
    downvotedLoading.value = false
  }
}

// 切换标签
const handleTabChange = (tab) => {
  activeTab.value = tab
  // 重置分页状态
  currentPage.value = 0
  hasMore.value = true

  // 根据标签加载对应内容
  switch (tab) {
    case 'posts':
      if (posts.value.length === 0) fetchUserPosts(true)
      break
    case 'comments':
      if (comments.value.length === 0) fetchUserComments(true)
      break
    case 'upvoted':
      if (upvoted.value.length === 0) fetchUserUpvoted(true)
      break
    case 'downvoted':
      if (downvoted.value.length === 0) fetchUserDownvoted(true)
      break
  }
}

// 点击帖子跳转到详情
const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}

// 点击社区跳转
const goToCommunity = (communityId) => {
  router.push(`/community/${communityId}`)
}

// 更新帖子投票状态
const updatePostVote = (postId, state) => {
  const post = posts.value.find(p => p.id === postId)
  if (post) {
    post.upvotes = state.upvotes
    post.downvotes = state.downvotes
    post.user_vote = state.userVote
    post.score = state.upvotes - state.downvotes
  }
}

// 更新帖子收藏状态
const updatePostBookmark = (postId, bookmarked, count) => {
  const post = posts.value.find(p => p.id === postId)
  if (post) {
    post.bookmarked = bookmarked
    post.bookmark_count = count
  }
}

// 加载更多
const loadMore = () => {
  switch (activeTab.value) {
    case 'posts':
      fetchUserPosts(false)
      break
    case 'comments':
      fetchUserComments(false)
      break
    case 'upvoted':
      fetchUserUpvoted(false)
      break
    case 'downvoted':
      fetchUserDownvoted(false)
      break
  }
}

// 重试加载
const retryLoad = () => {
  switch (activeTab.value) {
    case 'posts':
      fetchUserPosts(true)
      break
    case 'comments':
      fetchUserComments(true)
      break
    case 'upvoted':
      fetchUserUpvoted(true)
      break
    case 'downvoted':
      fetchUserDownvoted(true)
      break
  }
}

// 计算当前标签的加载状态
const currentLoading = computed(() => {
  switch (activeTab.value) {
    case 'posts': return postsLoading.value
    case 'comments': return commentsLoading.value
    case 'upvoted': return upvotedLoading.value
    case 'downvoted': return downvotedLoading.value
    default: return false
  }
})

// 计算当前标签的错误状态
const currentError = computed(() => {
  switch (activeTab.value) {
    case 'posts': return postsError.value
    case 'comments': return commentsError.value
    case 'upvoted': return upvotedError.value
    case 'downvoted': return downvotedError.value
    default: return null
  }
})

// 计算当前标签的数据
const currentData = computed(() => {
  switch (activeTab.value) {
    case 'posts': return posts.value
    case 'comments': return comments.value
    case 'upvoted': return upvoted.value
    case 'downvoted': return downvoted.value
    default: return []
  }
})

// 初始化
onMounted(() => {
  console.log('[UserDetail] 组件挂载，username:', username.value)
  fetchUserInfo()
  fetchUserPosts(true)
})
</script>

<template>
  <div class="user-detail-page">
    <!-- 用户信息卡片 -->
    <div v-if="userLoading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="userError" class="error-state">
      <p>{{ userError }}</p>
    </div>

    <div v-else-if="userInfo" class="user-info-card">
      <div class="user-avatar-section">
        <img
          v-if="userInfo.avatar"
          :src="userInfo.avatar"
          class="user-avatar-img"
          @error="handleAvatarError"
        />
        <div v-else class="user-avatar-text">
          {{ getAvatarText(userInfo) }}
        </div>
      </div>

      <div class="user-details">
        <h1 class="user-display-name">
          {{ userInfo.nickname || userInfo.username }}
        </h1>
        <p class="user-username">@{{ userInfo.username }}</p>

        <p v-if="userInfo.bio" class="user-bio">
          {{ userInfo.bio }}
        </p>

        <div class="user-stats">
          <div class="stat-item">
            <span class="stat-value">{{ userInfo.karma || 0 }}</span>
            <span class="stat-label">Karma</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ userInfo.post_count || 0 }}</span>
            <span class="stat-label">帖子</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ userInfo.comment_count || 0 }}</span>
            <span class="stat-label">评论</span>
          </div>
        </div>

        <div v-if="userInfo.created_at" class="user-joined">
          <Calendar :size="14" />
          <span>{{ formatJoinTime(userInfo.created_at) }}</span>
        </div>
      </div>
    </div>

    <!-- 标签页 -->
    <div v-if="userInfo" class="tabs-section">
      <UserTabs
        v-model="activeTab"
        :post-count="userInfo.post_count || 0"
        :comment-count="userInfo.comment_count || 0"
        @update:modelValue="handleTabChange"
      />
    </div>

    <!-- 内容区域 -->
    <div class="content-section">
      <!-- 帖子列表 -->
      <div v-if="activeTab === 'posts'">
        <div v-if="currentLoading && currentData.length === 0" class="loading-state">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="currentError" class="error-state">
          <p>{{ currentError }}</p>
          <button class="retry-btn" @click="retryLoad">重试</button>
        </div>

        <div v-else-if="currentData.length === 0" class="empty-state">
          <FileText :size="64" />
          <h3>还没有发布任何帖子</h3>
        </div>

        <div v-else>
          <div
            class="post-card"
            v-for="post in currentData"
            :key="post.id"
            @click="goToPost(post.id)"
          >
            <div class="post-content">
              <div class="post-header">
                <img
                  v-if="post.author?.avatar"
                  :src="post.author.avatar"
                  class="author-avatar author-avatar-img"
                  @error="handleAvatarError"
                />
                <div v-else class="author-avatar">{{ getAvatarText(post) }}</div>
                <span class="community-icon">👾</span>
                <span class="community-name" @click.stop="goToCommunity(post.community?.id)">
                  {{ post.community?.name || '未知社区' }}
                </span>
                <span class="meta-info">
                  · 由 {{ post.author?.username || '匿名用户' }} 发布 · {{ formatTime(post.created_at) }}
                </span>
              </div>

              <h3 class="post-title">{{ post.title }}</h3>

              <div class="post-preview" v-if="post.content">
                {{ renderPreview(post.content) }}
              </div>

              <div class="post-footer" @click.stop>
                <div class="footer-left">
                  <VoteButtons
                    :target-type="'post'"
                    :target-id="post.id"
                    :upvotes="post.upvotes || 0"
                    :downvotes="post.downvotes || 0"
                    :user-vote="post.user_vote || 0"
                    :show-count="true"
                    :icon-size="16"
                    @vote-change="(state) => updatePostVote(post.id, state)"
                  />

                  <BookmarkButton
                    :post-id="post.id"
                    :bookmarked="post.bookmarked || false"
                    :count="post.bookmark_count || 0"
                    :show-count="true"
                    :icon-size="16"
                    @bookmark-change="(b, c) => updatePostBookmark(post.id, b, c)"
                  />
                </div>

                <div class="footer-right">
                  <button class="action-btn" title="评论" @click.stop="goToPost(post.id)">
                    <MessageCircle :size="18" />
                    <span>{{ post.comment_count || 0 }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="hasMore" class="load-more-container">
            <button class="load-more-btn" @click="loadMore" :disabled="currentLoading">
              <span v-if="currentLoading">加载中...</span>
              <span v-else>加载更多</span>
            </button>
          </div>

          <div v-else-if="currentData.length > 0" class="no-more">
            <p>已经到底了</p>
          </div>
        </div>
      </div>

      <!-- 评论列表 -->
      <div v-if="activeTab === 'comments'">
        <div v-if="currentLoading && currentData.length === 0" class="loading-state">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="currentError" class="error-state">
          <p>{{ currentError }}</p>
          <button class="retry-btn" @click="retryLoad">重试</button>
        </div>

        <div v-else-if="currentData.length === 0" class="empty-state">
          <MessageCircle :size="64" />
          <h3>还没有发表任何评论</h3>
        </div>

        <div v-else>
          <div
            class="comment-card"
            v-for="comment in currentData"
            :key="comment.id"
          >
            <div class="comment-header">
              <img
                v-if="comment.author?.avatar"
                :src="comment.author.avatar"
                class="author-avatar author-avatar-img"
                @error="handleAvatarError"
              />
              <div v-else class="author-avatar">{{ getAvatarText({ author: comment.author }) }}</div>
              <span class="author-name">{{ comment.author?.username || '匿名用户' }}</span>
              <span class="comment-time">{{ formatTime(comment.created_at) }}</span>
            </div>

            <div class="comment-content" v-if="comment.content">
              {{ renderPreview(comment.content) }}
            </div>

            <div class="comment-post-link" @click="goToPost(comment.post_id)">
              <FileText :size="14" />
              <span>{{ comment.post?.title || '查看原帖' }}</span>
            </div>

            <div class="comment-footer">
              <div class="vote-info">
                <ThumbsUp :size="14" />
                <span>{{ comment.upvotes || 0 }}</span>
                <ThumbsDown :size="14" />
                <span>{{ comment.downvotes || 0 }}</span>
              </div>
            </div>
          </div>

          <div v-if="hasMore" class="load-more-container">
            <button class="load-more-btn" @click="loadMore" :disabled="currentLoading">
              <span v-if="currentLoading">加载中...</span>
              <span v-else>加载更多</span>
            </button>
          </div>

          <div v-else-if="currentData.length > 0" class="no-more">
            <p>已经到底了</p>
          </div>
        </div>
      </div>

      <!-- 点赞列表 -->
      <div v-if="activeTab === 'upvoted'">
        <div v-if="currentLoading && currentData.length === 0" class="loading-state">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="currentError" class="error-state">
          <p>{{ currentError }}</p>
          <button class="retry-btn" @click="retryLoad">重试</button>
        </div>

        <div v-else-if="currentData.length === 0" class="empty-state">
          <ThumbsUp :size="64" />
          <h3>还没有点赞任何内容</h3>
        </div>

        <div v-else>
          <div
            class="voted-item"
            v-for="item in currentData"
            :key="item.id"
            @click="goToPost(item.post_id || item.id)"
          >
            <div class="voted-icon">
              <ThumbsUp :size="16" />
            </div>
            <div class="voted-content">
              <div class="voted-title">{{ item.title || item.content?.substring(0, 100) }}</div>
              <div class="voted-meta">
                <span>{{ formatTime(item.created_at) }}</span>
                <span class="voted-type">{{ item.post_id ? '帖子' : '评论' }}</span>
              </div>
            </div>
          </div>

          <div v-if="hasMore" class="load-more-container">
            <button class="load-more-btn" @click="loadMore" :disabled="currentLoading">
              <span v-if="currentLoading">加载中...</span>
              <span v-else>加载更多</span>
            </button>
          </div>

          <div v-else-if="currentData.length > 0" class="no-more">
            <p>已经到底了</p>
          </div>
        </div>
      </div>

      <!-- 点踩列表 -->
      <div v-if="activeTab === 'downvoted'">
        <div v-if="currentLoading && currentData.length === 0" class="loading-state">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="currentError" class="error-state">
          <p>{{ currentError }}</p>
          <button class="retry-btn" @click="retryLoad">重试</button>
        </div>

        <div v-else-if="currentData.length === 0" class="empty-state">
          <ThumbsDown :size="64" />
          <h3>还没有点踩任何内容</h3>
        </div>

        <div v-else>
          <div
            class="voted-item"
            v-for="item in currentData"
            :key="item.id"
            @click="goToPost(item.post_id || item.id)"
          >
            <div class="voted-icon down">
              <ThumbsDown :size="16" />
            </div>
            <div class="voted-content">
              <div class="voted-title">{{ item.title || item.content?.substring(0, 100) }}</div>
              <div class="voted-meta">
                <span>{{ formatTime(item.created_at) }}</span>
                <span class="voted-type">{{ item.post_id ? '帖子' : '评论' }}</span>
              </div>
            </div>
          </div>

          <div v-if="hasMore" class="load-more-container">
            <button class="load-more-btn" @click="loadMore" :disabled="currentLoading">
              <span v-if="currentLoading">加载中...</span>
              <span v-else>加载更多</span>
            </button>
          </div>

          <div v-else-if="currentData.length > 0" class="no-more">
            <p>已经到底了</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-detail-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 20px;
}

/* 用户信息卡片 */
.user-info-card {
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  display: flex;
  gap: 20px;
}

.user-avatar-section {
  flex-shrink: 0;
}

.user-avatar-img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #edeff1;
}

.user-avatar-text {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: 700;
  border: 4px solid #edeff1;
}

.user-details {
  flex: 1;
}

.user-display-name {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #1c1c1c;
}

.user-username {
  font-size: 14px;
  color: #878a8c;
  margin: 0 0 12px 0;
}

.user-bio {
  font-size: 14px;
  color: #1c1c1c;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.user-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1c1c1c;
}

.stat-label {
  font-size: 12px;
  color: #878a8c;
  text-transform: uppercase;
}

.user-joined {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #878a8c;
  font-size: 13px;
}

/* 标签页区域 */
.tabs-section {
  margin-bottom: 20px;
}

.content-section {
  min-height: 300px;
}

/* 加载和错误状态 */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: #878a8c;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #edeff1;
  border-top-color: #0079d3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.retry-btn {
  padding: 10px 24px;
  background: #0079d3;
  color: #fff;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #0066b3;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1c1c1c;
  margin: 0;
}

/* 帖子卡片 */
.post-card {
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.post-card:hover {
  border-color: #0079d3;
}

.post-content {
  padding: 12px 16px;
}

.post-header {
  font-size: 12px;
  color: #787c7e;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #0079d3;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.author-avatar-img {
  background: transparent;
  object-fit: cover;
  border: 1px solid #e6e6e6;
}

.community-name {
  font-weight: 600;
  color: #0079d3;
  cursor: pointer;
}

.community-name:hover {
  text-decoration: underline;
}

.post-title {
  font-size: 18px;
  margin: 0 0 12px 0;
  font-weight: 600;
  color: #1c1c1c;
  line-height: 1.4;
}

.post-preview {
  color: #1c1c1c;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
  max-height: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #edeff1;
}

.footer-left {
  display: flex;
  gap: 4px;
}

.footer-right {
  display: flex;
  gap: 4px;
}

.action-btn {
  background: none;
  border: none;
  padding: 6px 12px;
  color: #878a8c;
  font-size: 13px;
  font-weight: 600;
  border-radius: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f6f7f8;
  color: #1c1c1c;
}

/* 评论卡片 */
.comment-card {
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.author-name {
  font-weight: 600;
  color: #1c1c1c;
  font-size: 14px;
}

.comment-time {
  color: #878a8c;
  font-size: 12px;
}

.comment-content {
  color: #1c1c1c;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
}

.comment-post-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f6f7f8;
  border-radius: 20px;
  color: #0079d3;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 8px;
}

.comment-post-link:hover {
  background: #edeff1;
}

.comment-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vote-info {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #878a8c;
  font-size: 12px;
}

.vote-info span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 点赞/点踩项 */
.voted-item {
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.voted-item:hover {
  border-color: #0079d3;
}

.voted-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #ff6b35;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.voted-icon.down {
  background: #878a8c;
}

.voted-content {
  flex: 1;
}

.voted-title {
  font-size: 14px;
  font-weight: 500;
  color: #1c1c1c;
  margin-bottom: 6px;
}

.voted-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #878a8c;
}

.voted-type {
  padding: 2px 8px;
  background: #f6f7f8;
  border-radius: 10px;
  font-weight: 600;
}

/* 加载更多 */
.load-more-container,
.no-more {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}

.load-more-btn {
  padding: 12px 32px;
  background: #fff;
  border: 1px solid #0079d3;
  border-radius: 24px;
  color: #0079d3;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-btn:hover:not(:disabled) {
  background: #0079d3;
  color: #fff;
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.no-more p {
  color: #878a8c;
  font-size: 14px;
  margin: 0;
}

/* 响应式 */
@media (max-width: 639px) {
  .user-detail-page {
    padding: 16px;
  }

  .user-info-card {
    padding: 16px;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .user-avatar-img,
  .user-avatar-text {
    width: 80px;
    height: 80px;
    font-size: 32px;
  }

  .user-stats {
    justify-content: center;
  }

  .user-joined {
    justify-content: center;
  }

  .post-card {
    border-radius: 0;
    border-left: none;
    border-right: none;
    margin-bottom: 0;
  }

  .post-content {
    padding: 12px;
  }

  .post-title {
    font-size: 16px;
  }

  .comment-card {
    padding: 12px;
  }

  .voted-item {
    padding: 12px;
  }
}
</style>
