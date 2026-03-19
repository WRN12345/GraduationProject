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

        <!-- 标题和状态 -->
        <div class="post-title-section">
          <div class="status-badges" v-if="post.is_pinned || post.is_highlighted">
            <span v-if="post.is_pinned" class="status-badge pinned-badge">
              <Pin :size="16" />
              <span>置顶</span>
            </span>
            <span v-if="post.is_highlighted" class="status-badge highlighted-badge">
              <Star :size="16" />
              <span>精华</span>
            </span>
          </div>
          <h1 class="post-title">{{ post.title }}</h1>
        </div>

        <!-- 作者信息 -->
        <div class="author-info" @click="goToAuthorProfile">
          <img
            v-if="post.author?.avatar"
            :src="post.author.avatar"
            class="author-avatar author-avatar-img"
            @error="handleAvatarError"
          />
          <div v-else class="author-avatar">{{ avatarText }}</div>
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

        <!-- 投票和收藏操作区 -->
        <div class="post-actions">
          <VoteButtons
            v-if="post"
            :target-type="'post'"
            :target-id="post.id"
            :upvotes="post.upvotes || 0"
            :downvotes="post.downvotes || 0"
            :user-vote="post.user_vote || 0"
            :show-count="true"
            :icon-size="18"
            @vote-change="handleVoteChange"
          />

          <BookmarkButton
            v-if="post"
            :post-id="post.id"
            :bookmarked="post.bookmarked || false"
            :count="post.bookmark_count || 0"
            :show-count="false"
            :icon-size="18"
          />
        </div>

        <!-- 帖主操作区 -->
        <div v-if="canEdit || canDelete" class="post-owner-actions">
          <button v-if="canEdit" class="action-btn edit-btn" @click="handleEdit">
            <Edit2 :size="16" />
            <span>编辑帖子</span>
          </button>
          <button v-if="canDelete" class="action-btn delete-btn" @click="handleDelete">
            <Trash2 :size="16" />
            <span>删除帖子</span>
          </button>
        </div>

        <!-- 版主操作区 -->
        <div v-if="isModerator" class="moderator-actions">
          <div class="moderator-actions-header">
            <h3>版主操作</h3>
          </div>
          <div class="moderator-actions-buttons">
            <button
              class="moderator-btn pin-btn"
              :class="{ active: post.is_pinned }"
              :disabled="loadingPin"
              @click="handleTogglePin"
            >
              <Pin :size="16" />
              <span v-if="!loadingPin">{{ post.is_pinned ? '取消置顶' : '置顶帖子' }}</span>
              <span v-else>处理中...</span>
            </button>
            <button
              class="moderator-btn highlight-btn"
              :class="{ active: post.is_highlighted }"
              :disabled="loadingHighlight"
              @click="handleToggleHighlight"
            >
              <Star :size="16" />
              <span v-if="!loadingHighlight">{{ post.is_highlighted ? '取消精华' : '设为精华' }}</span>
              <span v-else>处理中...</span>
            </button>
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
import { useRoute, useRouter } from 'vue-router'
import { Edit2, Trash2, Pin, Star } from 'lucide-vue-next'
import { ElMessageBox, ElMessage } from 'element-plus'
import { client } from '@/api/client'
import { marked } from 'marked'
import { useUserStore } from '@/stores/user'
import CommentTree from '@/components/comment/CommentTree.vue'
import VoteButtons from '@/components/VoteButtons.vue'
import BookmarkButton from '@/components/BookmarkButton.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const post = ref(null)
const loading = ref(true)
const membership = ref(null)  // 用户在社区的成员信息
const loadingPin = ref(false)  // 置顶操作加载状态
const loadingHighlight = ref(false)  // 精华操作加载状态

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

// 头像文字（用于没有头像时显示首字母）
const avatarText = computed(() => {
  const name = post.value?.author?.username || 'U'
  return name.charAt(0).toUpperCase()
})

// 权限检查
const canEdit = computed(() =>
  post.value && userStore.userId === post.value.author_id
)

const canDelete = computed(() =>
  post.value && userStore.userId === post.value.author_id
)

// 版主权限检查（owner或admin）
const isModerator = computed(() => {
  return membership.value?.role === 2 || membership.value?.role === 1
})

// 头像加载失败处理
const handleAvatarError = (event) => {
  // 图片加载失败时隐藏img元素，会自动显示首字母头像
  event.target.style.display = 'none'
}

// 跳转到作者主页
const goToAuthorProfile = () => {
  if (post.value?.author?.username) {
    router.push(`/user/${post.value.author.username}`)
  }
}

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

// 处理投票状态变化
const handleVoteChange = (state) => {
  if (post.value) {
    post.value.upvotes = state.upvotes
    post.value.downvotes = state.downvotes
    post.value.user_vote = state.userVote
    post.value.score = state.upvotes - state.downvotes
  }
}

// 删除帖子
const handleDelete = () => {
  ElMessageBox.confirm(
    '确定要删除这篇帖子吗？操作不可逆',
    '确认删除',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
      center: true,
      customClass: 'delete-confirm-box',
      draggable: false,
      closeOnClickModal: false,
      closeOnPressEscape: false
    }
  ).then(async () => {
    try {
      await client.DELETE('/v1/posts/{post_id}', {
        params: { path: { post_id: post.value.id } }
      })
      ElMessage.success('删除成功')
      router.push('/')
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {
    // 用户取消
  })
}

// 编辑帖子
const handleEdit = () => {
  router.push(`/post/${post.value.id}/edit`)
}

// 置顶/取消置顶帖子
const handleTogglePin = async () => {
  if (!post.value) return

  const newState = !post.value.is_pinned
  loadingPin.value = true

  try {
    const response = await client.PATCH('/v1/posts/{post_id}/pin', {
      params: {
        path: { post_id: post.value.id },
        query: { is_pinned: newState }
      }
    })

    if (response.data) {
      // 更新本地状态
      post.value.is_pinned = newState
      ElMessage.success(newState ? '帖子已置顶' : '已取消置顶')
    }
  } catch (error) {
    console.error('置顶操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  } finally {
    loadingPin.value = false
  }
}

// 精华/取消精华帖子
const handleToggleHighlight = async () => {
  if (!post.value) return

  const newState = !post.value.is_highlighted
  loadingHighlight.value = true

  try {
    const response = await client.PATCH('/v1/posts/{post_id}/highlight', {
      params: {
        path: { post_id: post.value.id },
        query: { is_highlighted: newState }
      }
    })

    if (response.data) {
      // 更新本地状态
      post.value.is_highlighted = newState
      ElMessage.success(newState ? '已设置精华' : '已取消精华')
    }
  } catch (error) {
    console.error('精华操作失败:', error)
    ElMessage.error('操作失败，请稍后重试')
  } finally {
    loadingHighlight.value = false
  }
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

      // 获取用户在该社区的角色信息
      if (userStore.isLoggedIn) {
        try {
          const myCommunitiesResponse = await client.GET('/v1/memberships/my-communities')
          if (myCommunitiesResponse.data) {
            const found = myCommunitiesResponse.data.find(c => c.id === post.value.community_id)
            if (found) {
              membership.value = { role: found.role }
            }
          }
        } catch (err) {
          console.error('[PostDetail] 获取社区角色失败:', err)
        }
      }

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

.post-title-section {
  margin-bottom: 20px;
}

.status-badges {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  line-height: 1;
}

.pinned-badge {
  background: #fff5f5;
  color: #ff4500;
  border: 1px solid #ffccc7;
}

.highlighted-badge {
  background: #fffff0;
  color: #ffa500;
  border: 1px solid #ffe58f;
}

.post-title {
  font-size: 28px;
  font-weight: 700;
  color: #1c1c1c;
  margin: 0;
  line-height: 1.3;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.author-info:hover {
  opacity: 0.8;
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

.author-avatar-img {
  background: transparent;
  object-fit: cover;
  border: 2px solid #e6e6e6;
}

.author-details {
  flex: 1;
}

.author-name {
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
  transition: color 0.2s;
}

.author-name:hover {
  color: #0079d3;
  text-decoration: underline;
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

/* 操作按钮区 */
.post-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  margin: 20px 0;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.post-actions:hover {
  border-color: #dee2e6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.post-actions > * {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 帖主操作区 */
.post-owner-actions {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  margin: 20px 0;
  background: #fff8f8;
  border-radius: 12px;
  border: 1px solid #ffebee;
}

.post-owner-actions .action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-btn {
  background: #e3f2fd;
  color: #1976d2;
}

.edit-btn:hover {
  background: #bbdefb;
}

.delete-btn {
  background: #ffebee;
  color: #d32f2f;
}

.delete-btn:hover {
  background: #ffcdd2;
}

/* 版主操作区 */
.moderator-actions {
  padding: 16px 20px;
  margin: 20px 0;
  background: #f0f7ff;
  border-radius: 12px;
  border: 1px solid #b3d9ff;
}

.moderator-actions-header {
  margin-bottom: 12px;
}

.moderator-actions-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: #0052a3;
  margin: 0;
}

.moderator-actions-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.moderator-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  border: 2px solid;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.moderator-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.pin-btn {
  border-color: #ff4500;
  color: #ff4500;
}

.pin-btn:hover:not(:disabled) {
  background: #fff5f5;
}

.pin-btn.active {
  background: #ff4500;
  color: white;
}

.highlight-btn {
  border-color: #ffa500;
  color: #ffa500;
}

.highlight-btn:hover:not(:disabled) {
  background: #fffff0;
}

.highlight-btn.active {
  background: #ffa500;
  color: white;
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

  .post-actions {
    padding: 12px 16px;
    margin: 16px 0;
    border-radius: 8px;
  }
}
</style>
