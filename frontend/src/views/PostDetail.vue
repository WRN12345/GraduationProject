<template>
  <div class="post-detail-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="post" class="post-detail-card">
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

        <!-- 附件列表 -->
        <div v-if="post.attachments && post.attachments.length > 0" class="post-attachments-section">
          <h4>附件 ({{ post.attachments.length }})</h4>
          <div class="attachments-list">
            <!-- 图片附件 -->
            <div
              v-for="attachment in post.attachments.filter(a => a.attachment_type === 'image')"
              :key="attachment.id"
              class="attachment-item image-attachment"
            >
              <img :src="attachment.file_url" :alt="attachment.file_name" @click="viewImage(attachment.file_url)" />
              <div class="attachment-info">
                <span class="file-name">{{ attachment.file_name }}</span>
                <span class="file-size">{{ formatFileSize(attachment.file_size) }}</span>
              </div>
            </div>
            <!-- 视频附件 -->
            <div
              v-for="attachment in post.attachments.filter(a => a.attachment_type === 'video')"
              :key="attachment.id"
              class="attachment-item video-attachment"
            >
              <video :src="attachment.file_url" controls />
              <div class="attachment-info">
                <span class="file-name">{{ attachment.file_name }}</span>
                <span class="file-size">{{ formatFileSize(attachment.file_size) }}</span>
              </div>
            </div>
            <!-- 文件附件 -->
            <div
              v-for="attachment in post.attachments.filter(a => a.attachment_type === 'file')"
              :key="attachment.id"
              class="attachment-item file-attachment"
            >
              <div class="file-icon">📄</div>
              <div class="attachment-info">
                <span class="file-name">{{ attachment.file_name }}</span>
                <span class="file-size">{{ formatFileSize(attachment.file_size) }}</span>
              </div>
              <button class="download-btn" @click="downloadFile(attachment)">下载</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 评论区 -->
      <div class="comments-section">
        <CommentTree v-if="post" :post-id="post.id" />
      </div>
    </div>

    <div v-else class="error-state">
      <p>帖子不存在或已被删除</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { client } from '@/api/client'
import { marked } from 'marked'
import CommentTree from '@/components/comment/CommentTree.vue'

const route = useRoute()

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

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 查看图片
const viewImage = (url) => {
  window.open(url, '_blank')
}

// 下载文件
const downloadFile = (attachment) => {
  const link = document.createElement('a')
  link.href = attachment.file_url
  link.download = attachment.file_name
  link.click()
}

// 加载帖子详情
const loadPost = async () => {
  const postId = route.params.id
  console.log('[PostDetail] 加载帖子, ID:', postId, '类型:', typeof postId)

  // 验证 ID 是否有效
  const parsedId = parseInt(postId)
  if (isNaN(parsedId)) {
    console.error('[PostDetail] 无效的帖子 ID:', postId)
    loading.value = false
    return
  }

  loading.value = true
  try {
    const response = await client.GET('/v1/posts/{post_id}', {
      params: {
        path: { post_id: parsedId }
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

/* 附件区域 */
.post-attachments-section {
  margin-top: 24px;
  padding: 16px;
  background: #f6f7f8;
  border-radius: 8px;
}

.post-attachments-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #1c1c1c;
  font-weight: 600;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.image-attachment {
  flex-direction: column;
  align-items: flex-start;
}

.image-attachment img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.image-attachment img:hover {
  transform: scale(1.02);
}

.video-attachment {
  flex-direction: column;
  align-items: flex-start;
}

.video-attachment video {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.file-attachment {
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #edeff1;
}

.file-icon {
  font-size: 32px;
}

.attachment-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #1c1c1c;
  word-break: break-all;
}

.file-size {
  font-size: 12px;
  color: #878a8c;
}

.download-btn {
  padding: 8px 16px;
  background: #0079d3;
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.download-btn:hover {
  background: #0066b3;
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
