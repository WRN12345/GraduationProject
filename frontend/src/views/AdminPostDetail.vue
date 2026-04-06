<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { marked } from 'marked'
import { ArrowLeft, Edit2, Trash2, Pin, Star, Settings, ChevronDown } from 'lucide-vue-next'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getPostDetail, deletePost, restorePost, hardDeletePost } from '@/api/admin'
import { useFormatTime } from '@/composables/useFormatTime'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { formatTime } = useFormatTime()

const postId = computed(() => route.params.id)
const loading = ref(true)
const post = ref(null)
const error = ref(null)

// 渲染 Markdown 内容
const renderedContent = computed(() => {
  if (!post.value?.content) return ''
  return marked(post.value.content)
})

// 检查是否是已删除帖子
const isDeleted = computed(() => !!post.value?.deleted_at)

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return `${bytes.toFixed(1)} ${units[i]}`
}

// 查看图片
const viewImage = (url) => {
  window.open(url, '_blank')
}

// 下载文件
const downloadFile = (attachment) => {
  window.open(attachment.file_url, '_blank')
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 软删除帖子
const handleSoftDelete = async () => {
  try {
    await ElMessageBox.confirm(
      t('admin.posts.confirmDelete'),
      t('common.confirm'),
      { confirmButtonText: t('admin.posts.deleteBtn'), cancelButtonText: t('common.cancel'), type: 'warning' }
    )
    await deletePost(postId.value)
    ElMessage.success(t('admin.posts.deleteSuccess'))
    // 刷新数据
    await fetchPostDetail()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(t('admin.posts.operationFailed'))
    }
  }
}

// 恢复帖子
const handleRestore = async () => {
  try {
    await ElMessageBox.confirm(
      t('admin.posts.confirmRestore'),
      t('common.confirm'),
      { confirmButtonText: t('admin.posts.restoreBtn'), cancelButtonText: t('common.cancel'), type: 'info' }
    )
    await restorePost(postId.value)
    ElMessage.success(t('admin.posts.restoreSuccess'))
    // 刷新数据
    await fetchPostDetail()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(t('admin.posts.operationFailed'))
    }
  }
}

// 硬删除帖子
const handleHardDelete = async () => {
  try {
    await ElMessageBox.confirm(
      t('admin.posts.confirmHardDelete'),
      t('common.confirm'),
      { confirmButtonText: t('admin.posts.hardDeleteBtn'), cancelButtonText: t('common.cancel'), type: 'error' }
    )
    await hardDeletePost(postId.value)
    ElMessage.success(t('admin.posts.hardDeleteSuccess'))
    // 跳回帖子列表
    router.push('/admin/posts')
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(t('admin.posts.operationFailed'))
    }
  }
}

// 获取帖子详情
const fetchPostDetail = async () => {
  loading.value = true
  error.value = null
  try {
    const data = await getPostDetail(postId.value)
    post.value = data
  } catch (e) {
    error.value = e.message || t('common.error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPostDetail()
})
</script>

<template>
  <div class="admin-post-detail-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ t('postDetail.loading') }}</p>
    </div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <el-button @click="goBack">{{ t('common.back') }}</el-button>
    </div>

    <div v-else-if="post" class="post-detail-layout">
      <!-- 页面头部 -->
      <div class="page-header">
        <el-button class="back-btn" @click="goBack">
          <ArrowLeft :size="18" />
          <span>{{ t('common.back') }}</span>
        </el-button>
        <div class="admin-badges">
          <el-tag v-if="isDeleted" type="danger" size="large">
            {{ t('admin.posts.statusDeleted') }}
          </el-tag>
          <el-tag v-if="post.is_pinned" type="warning" size="large">
            <Pin :size="14" />
            {{ t('postDetail.pinned') }}
          </el-tag>
          <el-tag v-if="post.is_highlighted" type="success" size="large">
            <Star :size="14" />
            {{ t('postDetail.highlighted') }}
          </el-tag>
        </div>
        <div class="header-actions">
          <el-button v-if="isDeleted" type="success" @click="handleRestore">
            {{ t('admin.posts.restoreBtn') }}
          </el-button>
          <el-button v-if="isDeleted" type="danger" @click="handleHardDelete">
            {{ t('admin.posts.hardDeleteBtn') }}
          </el-button>
          <el-button v-else type="danger" @click="handleSoftDelete">
            {{ t('admin.posts.deleteBtn') }}
          </el-button>
        </div>
      </div>

      <!-- 帖子内容卡片 -->
      <div class="post-detail-card">
        <!-- 社区信息 -->
        <div class="community-info">
          <span class="community-icon">👾</span>
          <span class="community-name">{{ post.community?.name || t('postDetail.unknownCommunity') }}</span>
          <span class="separator">•</span>
          <span class="post-time">{{ formatTime(post.created_at) }}</span>
          <span v-if="post.is_edited" class="edited-badge">({{ t('postDetail.edited') }})</span>
        </div>

        <!-- 标题 -->
        <h1 class="post-title">{{ post.title }}</h1>

        <!-- 作者信息 -->
        <div class="author-info">
          <div class="author-avatar">{{ post.author?.username?.charAt(0).toUpperCase() }}</div>
          <div class="author-details">
            <div class="author-name">{{ post.author?.username || t('postDetail.anonymousUser') }}</div>
            <div class="post-meta">
              <span>{{ post.score || 0 }} {{ t('postDetail.score') }}</span>
              <span class="separator">•</span>
              <span>{{ post.comment_count || 0 }} {{ t('postDetail.comments') }}</span>
            </div>
          </div>
        </div>

        <hr class="divider" />

        <!-- 内容 -->
        <div class="content-body markdown-content" v-html="renderedContent"></div>

        <!-- 附件列表 -->
        <div v-if="post.attachments && post.attachments.length > 0" class="post-attachments-section">
          <h3>{{ t('postDetail.attachments') }}</h3>
          <div class="attachments-list">
            <!-- 图片附件 -->
            <div
              v-for="attachment in post.attachments.filter(a => a.attachment_type === 'image')"
              :key="attachment.id"
              class="attachment-item image-attachment"
            >
              <img :src="attachment.file_url" :alt="attachment.file_name" @click="viewImage(attachment.file_url)" />
            </div>
            <!-- 视频附件 -->
            <div
              v-for="attachment in post.attachments.filter(a => a.attachment_type === 'video')"
              :key="attachment.id"
              class="attachment-item video-attachment"
            >
              <video :src="attachment.file_url" controls class="video-player" />
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
              <button class="download-btn" @click="downloadFile(attachment)">{{ t('postDetail.download') }}</button>
            </div>
          </div>
        </div>

        <!-- 删除信息 -->
        <div v-if="isDeleted" class="deleted-info">
          <el-tag type="danger">{{ t('admin.posts.deletedAt') }}: {{ formatTime(post.deleted_at) }}</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-post-detail-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color-light);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

.admin-badges {
  display: flex;
  gap: 8px;
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.post-detail-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color-light);
  border-radius: 12px;
  padding: 24px;
}

.community-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 16px;
}

.community-icon {
  font-size: 18px;
}

.community-name {
  font-weight: 500;
  color: var(--color-primary);
  cursor: pointer;
}

.separator {
  color: var(--text-tertiary);
}

.post-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 20px;
  line-height: 1.3;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  cursor: pointer;
}

.author-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 18px;
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-weight: 600;
  color: var(--text-primary);
}

.post-meta {
  font-size: 13px;
  color: var(--text-secondary);
}

.divider {
  border: none;
  border-top: 1px solid var(--border-color-light);
  margin: 20px 0;
}

.content-body {
  font-size: 16px;
  line-height: 1.7;
  color: var(--text-primary);
}

.content-body :deep(h1),
.content-body :deep(h2),
.content-body :deep(h3) {
  margin: 1em 0 0.5em;
  font-weight: 600;
}

.content-body :deep(p) {
  margin: 0.8em 0;
}

.content-body :deep(pre) {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 14px;
}

.content-body :deep(code) {
  background: var(--bg-secondary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.content-body :deep(ul),
.content-body :deep(ol) {
  padding-left: 24px;
}

.content-body :deep(blockquote) {
  border-left: 4px solid var(--color-primary);
  margin: 1em 0;
  padding-left: 16px;
  color: var(--text-secondary);
}

.edited-badge {
  font-size: 12px;
  color: var(--text-tertiary);
}

.post-attachments-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color-light);
}

.post-attachments-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attachment-item img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  cursor: pointer;
}

.video-player {
  width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.file-attachment {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.file-icon {
  font-size: 24px;
}

.attachment-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.file-name {
  font-weight: 500;
  color: var(--text-primary);
}

.file-size {
  font-size: 12px;
  color: var(--text-secondary);
}

.download-btn {
  padding: 8px 16px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.download-btn:hover {
  opacity: 0.9;
}

.deleted-info {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color-light);
}
</style>