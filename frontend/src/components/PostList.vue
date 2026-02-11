<template>
  <div class="post-list">
    <!-- 加载状态 -->
    <div v-if="loading && posts.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadPosts(true)">重试</button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="posts.length === 0" class="empty-state">
      <ArrowBigUp :size="64" />
      <h3>{{ emptyTitle }}</h3>
      <p>{{ emptyMessage }}</p>
    </div>

    <!-- 帖子列表 -->
    <div v-else>
      <div
        class="post-card"
        v-for="post in displayPosts"
        :key="post.id"
        @click="goToPost(post.id)"
      >
        <!-- 帖子内容 -->
        <div class="post-content">
          <div class="post-header">
            <span class="community-icon">👾</span>
            <span class="community-name" @click.stop="goToCommunity(post.community?.id)">
              {{ post.community?.name || '未知社区' }}
            </span>
            <span class="meta-info">· 由 {{ post.author?.username || '匿名用户' }} 发布 · {{ formatTime(post.created_at) }}</span>
          </div>

          <h3 class="post-title">{{ post.title }}</h3>

          <!-- 内容预览 -->
          <div class="post-preview" v-if="post.content">
            {{ renderPreview(post.content) }}
          </div>

          <!-- 底部操作区 -->
          <div class="post-footer" @click.stop>
            <!-- 左侧：点赞点踩 -->
            <div class="footer-left">
              <button class="vote-action-btn" :class="{ active: post.upvotes > 0 }">
                <ThumbsUp :size="18" />
                <span>{{ post.upvotes || 0 }}</span>
              </button>
              <button class="vote-action-btn">
                <ThumbsDown :size="18" />
              </button>
            </div>

            <!-- 右侧：评论收藏转发 -->
            <div class="footer-right">
              <button class="action-btn" title="评论">
                <MessageCircle :size="18" />
                <span>{{ post.comment_count || 0 }}</span>
              </button>
              <button class="action-btn" title="收藏">
                <Bookmark :size="18" />
              </button>
              <button class="action-btn" title="转发">
                <Share2 :size="18" />
              </button>
            </div>
          </div>

          <!-- 评论输入框 -->
          <div class="comment-input-wrapper" @click.stop>
            <div class="comment-input">
              <input
                type="text"
                v-model="commentInputs[post.id]"
                placeholder="善语结善缘，恶语伤人心"
                class="comment-field"
              />
              <button class="send-btn" title="发送" :disabled="!commentInputs[post.id]?.trim()">
                <Send :size="16" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore" class="load-more-container">
        <button
          class="load-more-btn"
          @click="loadMore"
          :disabled="loading"
        >
          <span v-if="loading">加载中...</span>
          <span v-else>加载更多</span>
        </button>
      </div>

      <div v-else-if="posts.length > 0" class="no-more">
        <p>已经到底了</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  ThumbsUp,
  ThumbsDown,
  MessageCircle,
  Bookmark,
  Share2,
  Send,
  ArrowBigUp
} from 'lucide-vue-next'
import { client } from '@/api/client'
import { marked } from 'marked'

const props = defineProps({
  communityId: {
    type: Number,
    default: null  // null 表示获取所有帖子
  },
  emptyTitle: {
    type: String,
    default: '还没有帖子'
  },
  emptyMessage: {
    type: String,
    default: '成为第一个发布内容的人吧！'
  }
})

const router = useRouter()

// 状态
const posts = ref([])
const loading = ref(false)
const error = ref(null)

// 分页
const currentPage = ref(0)
const pageSize = 20
const hasMore = ref(true)

// 评论输入
const commentInputs = ref({})

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

// 格式化时间
const formatTime = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  const now = new Date()
  const diff = (now - date) / 1000 // 秒

  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  if (diff < 604800) return `${Math.floor(diff / 86400)} 天前`

  return date.toLocaleDateString('zh-CN')
}

// 渲染 Markdown（预览，只显示前200个字符）
const renderPreview = (content) => {
  if (!content) return ''
  try {
    const html = marked(content)
    // 移除 HTML 标签获取纯文本，然后截取前 200 个字符
    const text = html.replace(/<[^>]*>/g, '')
    return text.length > 200 ? text.substring(0, 200) + '...' : text
  } catch (error) {
    console.error('[PostList] Markdown 渲染错误:', error)
    return content?.substring(0, 200) || ''
  }
}

// 加载帖子列表
const loadPosts = async (reset = false) => {
  if (loading.value) return
  if (reset) {
    currentPage.value = 0
    posts.value = []
    hasMore.value = true
  }

  if (!hasMore.value) return

  loading.value = true
  error.value = null

  try {
    const params = {
      query: {
        skip: currentPage.value * pageSize,
        limit: pageSize
      }
    }

    if (props.communityId) {
      params.query.community_id = props.communityId
    }

    const response = await client.GET('/v1/posts', { params })

    if (response.data) {
      console.log('[PostList] 加载成功，帖子数量:', response.data.items?.length || 0)

      if (response.data.items) {
        // 分页格式
        posts.value = reset ? response.data.items : [...posts.value, ...response.data.items]
        hasMore.value = response.data.has_more ?? (response.data.items.length >= pageSize)
        currentPage.value++
      } else {
        // 直接数组格式
        posts.value = reset ? response.data : [...posts.value, ...response.data]
        hasMore.value = response.data.length >= pageSize
        currentPage.value++
      }
    }
  } catch (err) {
    console.error('[PostList] 加载失败:', err)
    error.value = '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 点击帖子跳转到详情
const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}

// 点击社区跳转
const goToCommunity = (communityId) => {
  // 跳转到社区详情页
  router.push(`/community/${communityId}`)
}

// 加载更多
const loadMore = () => {
  loadPosts(false)
}

// 初始化
onMounted(() => {
  console.log('[PostList] 组件挂载，communityId:', props.communityId)
  loadPosts(true)
})

// 计算属性
const displayPosts = computed(() => posts.value)

// 暴露方法供父组件调用
defineExpose({
  loadPosts,
  refresh: () => loadPosts(true)
})
</script>

<style scoped>
/* 加载状态 */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
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
  font-size: 20px;
  font-weight: 600;
  color: #1c1c1c;
  margin: 0;
}

.empty-state p {
  font-size: 14px;
  color: #878a8c;
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

/* 底部操作区 */
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

.vote-action-btn {
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

.vote-action-btn:hover {
  background: #f6f7f8;
  color: #1c1c1c;
}

.vote-action-btn.active {
  color: #0079d3;
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

/* 评论输入框 */
.comment-input-wrapper {
  margin-top: 12px;
}

.comment-input {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f6f7f8;
  border: 1px solid transparent;
  border-radius: 24px;
  padding: 8px 16px;
  transition: all 0.2s;
}

.comment-input:focus-within {
  background: #fff;
  border-color: #0079d3;
  box-shadow: 0 0 0 2px rgba(0, 121, 211, 0.1);
}

.comment-field {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  color: #1c1c1c;
}

.comment-field::placeholder {
  color: #878a8c;
  font-style: italic;
}

.send-btn {
  background: none;
  border: none;
  color: #0079d3;
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: rgba(0, 121, 211, 0.1);
}

.send-btn:disabled {
  color: #ccc;
  cursor: not-allowed;
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

/* === 响应式优化 === */

/* 小窗口 (< 640px) */
@media (max-width: 639px) {
  .post-card {
    border-radius: 0;
    border-left: none;
    border-right: none;
    margin-bottom: 0;
  }

  .post-card:first-child {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }

  .post-content {
    padding: 12px;
  }

  .post-title {
    font-size: 16px;
  }

  .post-footer {
    flex-wrap: wrap;
    gap: 4px;
  }

  .footer-left,
  .footer-right {
    gap: 2px;
  }

  .vote-action-btn,
  .action-btn {
    padding: 6px 8px;
    font-size: 12px;
  }

  .comment-input {
    padding: 6px 12px;
  }
}
</style>
