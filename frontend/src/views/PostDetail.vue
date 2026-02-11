<template>
  <div class="post-detail-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="post" class="post-detail-card">
      <!-- 头部操作栏 -->
      <div class="detail-header">
        <button class="back-btn" @click="goBack">
          <ArrowLeft :size="20" />
          <span>返回</span>
        </button>
      </div>

      <!-- 帖子内容 -->
      <div class="post-content">
        <!-- 社区信息 -->
        <div class="community-info">
          <span class="community-icon">👾</span>
          <span class="community-name">{{ post.community?.name || '未知社区' }}</span>
          <span class="separator">•</span>
          <span class="post-time">{{ formatTime(post.created_at) }}</span>
        </div>

        <!-- 标题 -->
        <h1 class="post-title">{{ post.title }}</h1>

        <!-- 作者信息 -->
        <div class="author-info">
          <div class="author-avatar">{{ post.author?.username?.charAt(0).toUpperCase() || '?' }}</div>
          <div class="author-details">
            <div class="author-name">{{ post.author?.username || '匿名用户' }}</div>
            <div class="post-meta">
              <span>{{ post.score || 0 }} 分</span>
              <span class="separator">•</span>
              <span>{{ post.upvotes || 0 }} 赞</span>
            </div>
          </div>
        </div>

        <hr class="divider" />

        <!-- 内容 -->
        <div class="content-body markdown-content" v-html="renderedContent"></div>
      </div>

      <!-- 评论区占位 -->
      <div class="comments-section">
        <p class="comments-placeholder">评论功能即将推出...</p>
      </div>
    </div>

    <div v-else class="error-state">
      <p>帖子不存在或已被删除</p>
      <button class="back-btn" @click="goBack">返回首页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from 'lucide-vue-next'
import { client } from '@/api/client'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()

const post = ref(null)
const loading = ref(true)

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

// 渲染 Markdown
const renderedContent = computed(() => {
  if (!post.value?.content) return ''
  try {
    return marked(post.value.content)
  } catch (error) {
    console.error('Markdown 渲染错误:', error)
    return '<p>渲染错误</p>'
  }
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

// 加载帖子详情
const loadPost = async () => {
  const postId = route.params.id
  console.log('[PostDetail] 加载帖子, ID:', postId)

  loading.value = true
  try {
    const response = await client.GET('/v1/posts/{post_id}', {
      params: {
        path: { post_id: parseInt(postId) }
      }
    })

    if (response.data) {
      post.value = response.data
      console.log('[PostDetail] 加载成功')
    } else {
      console.log('[PostDetail] 帖子不存在')
    }
  } catch (error) {
    console.error('[PostDetail] 加载失败:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

onMounted(() => {
  loadPost()
})
</script>

<style scoped>
.post-detail-container {
  min-height: calc(100vh - 56px);
  padding: 24px 16px;
  background: #f6f7f8;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #878a8c;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #edeff1;
  border-top-color: #0079d3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.post-detail-card {
  max-width: 800px;
  margin: 0 auto;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.detail-header {
  padding: 16px 24px;
  border-bottom: 1px solid #edeff1;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #f6f7f8;
  color: #1c1c1c;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #edeff1;
}

.post-content {
  padding: 24px;
}

.community-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 14px;
}

.community-icon {
  font-size: 20px;
}

.community-name {
  font-weight: 600;
  color: #0079d3;
}

.separator {
  color: #edeff1;
}

.post-time {
  color: #878a8c;
}

.post-title {
  font-size: 28px;
  font-weight: 700;
  color: #1c1c1c;
  margin: 0 0 20px 0;
  line-height: 1.3;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #0079d3;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
}

.author-details {
  flex: 1;
}

.author-name {
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
}

.post-meta {
  font-size: 12px;
  color: #878a8c;
  margin-top: 2px;
}

.divider {
  border: none;
  border-top: 1px solid #edeff1;
  margin: 16px 0;
}

.content-body {
  font-size: 16px;
  line-height: 1.6;
  color: #1c1c1c;
}

/* Markdown 样式 */
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
}

.markdown-content :deep(h1) {
  font-size: 2em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid #edeff1;
}

.markdown-content :deep(h2) {
  font-size: 1.5em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid #edeff1;
}

.markdown-content :deep(p) {
  margin: 0 0 16px 0;
}

.markdown-content :deep(code) {
  background: #f6f7f8;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background: #f6f7f8;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0 0 16px 0;
}

.markdown-content :deep(pre code) {
  background: transparent;
  padding: 0;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #0079d3;
  padding-left: 16px;
  margin: 0 0 16px 0;
  color: #878a8c;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0 0 16px 0;
  padding-left: 24px;
}

.markdown-content :deep(li) {
  margin: 4px 0;
}

.markdown-content :deep(a) {
  color: #0079d3;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.markdown-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 16px 0;
}

.comments-section {
  padding: 24px;
  border-top: 1px solid #edeff1;
  background: #f6f7f8;
}

.comments-placeholder {
  text-align: center;
  color: #878a8c;
  font-size: 14px;
  font-style: italic;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 16px;
  color: #878a8c;
}

/* 响应式 */
@media (max-width: 639px) {
  .post-detail-container {
    padding: 16px 8px;
  }

  .post-content {
    padding: 16px;
  }

  .post-title {
    font-size: 24px;
  }

  .content-body {
    font-size: 15px;
  }
}
</style>
