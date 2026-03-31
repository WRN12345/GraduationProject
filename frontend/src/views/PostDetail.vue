<template>
  <div class="post-detail-container">
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>{{ $t('postDetail.loading') }}</p>
    </div>

    <div v-else-if="post" class="post-detail-card">
      <!-- 帖子内容 -->
      <div class="post-content">
        <!-- 社区信息 -->
        <div class="community-info">
          <span class="community-icon">👾</span>
          <a class="community-name" @click="goToCommunity">{{ post.community?.name || $t('postDetail.unknownCommunity') }}</a>
          <span class="separator">•</span>
          <span class="post-time">{{ formatTime(post.created_at) }}</span>

          <!-- 作者专属操作按钮 - 编辑和删除 -->
          <div v-if="canEdit || canDelete" class="author-actions">
            <button v-if="canEdit" class="author-action-btn" @click="handleEdit" :title="$t('postDetail.editPost')">
              <Edit2 :size="14" />
              <span>{{ $t('common.edit') }}</span>
            </button>
            <button v-if="canDelete" class="author-action-btn delete" @click="handleDelete" :title="$t('postDetail.deletePost')">
              <Trash2 :size="14" />
              <span>{{ $t('common.delete') }}</span>
            </button>
          </div>
        </div>

        <!-- 标题和状态 -->
        <div class="post-title-section">
          <div class="status-badges" v-if="post.is_pinned || post.is_highlighted">
            <span v-if="post.is_pinned" class="status-badge pinned-badge">
              <Pin :size="16" />
              <span>{{ $t('postDetail.pinned') }}</span>
            </span>
            <span v-if="post.is_highlighted" class="status-badge highlighted-badge">
              <Star :size="16" />
              <span>{{ $t('postDetail.highlighted') }}</span>
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
            <div class="author-name">{{ post.author?.username || $t('postDetail.anonymousUser') }}</div>
            <div class="post-meta">
              <span>{{ post.score || 0 }} {{ $t('postDetail.score') }}</span>
              <span class="separator">•</span>
              <span>{{ post.upvotes || 0 }} {{ $t('postDetail.upvotes') }}</span>
            </div>
          </div>
        </div>

        <hr class="divider" />

        <!-- 内容 -->
        <div class="content-body markdown-content" v-html="renderedContent"></div>

        <!-- 附件列表 -->
        <div v-if="post.attachments && post.attachments.length > 0" class="post-attachments-section">
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
              <button class="download-btn" @click="downloadFile(attachment)">{{ $t('postDetail.download') }}</button>
            </div>
          </div>
        </div>

        <!-- 互动操作区 -->
        <div class="post-actions">
          <div class="actions-left">
            <!-- 投票按钮 -->
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

            <!-- 收藏按钮 -->
            <BookmarkButton
              v-if="post"
              :post-id="post.id"
              :bookmarked="post.bookmarked || false"
              :count="post.bookmark_count || 0"
              :show-count="false"
              :icon-size="18"
            />

            <!-- 转发按钮 -->
            <button class="action-btn" :title="$t('postDetail.share')">
              <Share2 :size="18" />
            </button>
          </div>

          <!-- 版主操作 - 右侧下拉菜单 -->
          <div v-if="isModerator" class="actions-right">
            <el-dropdown trigger="click" @command="handleModeratorCommand">
              <button class="moderator-dropdown-btn" :disabled="loadingPin || loadingHighlight">
                <Settings :size="16" />
                <span v-if="loadingPin || loadingHighlight">{{ $t('postDetail.processing') }}</span>
                <span v-else>{{ $t('postDetail.moderatorActions') }}</span>
                <ChevronDown :size="14" />
              </button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="'pin'">
                    <Pin :size="14" />
                    <span>{{ post.is_pinned ? $t('postDetail.unpin') : $t('postDetail.pinPost') }}</span>
                  </el-dropdown-item>
                  <el-dropdown-item :command="'highlight'">
                    <Star :size="14" />
                    <span>{{ post.is_highlighted ? $t('postDetail.unhighlight') : $t('postDetail.setHighlight') }}</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>

      <!-- 评论区 -->
      <div class="comments-section">
        <CommentTree v-if="post" :post-id="post.id" />
      </div>
    </div>

    <div v-else class="error-state">
      <p>{{ $t('postDetail.postNotFound') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Edit2, Trash2, Pin, Star, Share2, Settings, ChevronDown, Play } from 'lucide-vue-next'
import { ElMessageBox, ElMessage, ElDropdown, ElDropdownMenu, ElDropdownItem } from 'element-plus'
import { client } from '@/api/client'
import { marked } from 'marked'
import { useUserStore } from '@/stores/user'
import CommentTree from '@/components/comment/CommentTree.vue'
import VoteButtons from '@/components/VoteButtons.vue'
import BookmarkButton from '@/components/BookmarkButton.vue'
import { useFormatTime } from '@/composables/useFormatTime'

const { t } = useI18n()
const { formatTime } = useFormatTime()

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const post = ref(null)
const loading = ref(true)
const membership = ref(null)  // 用户在社区的成员信息
const loadingPin = ref(false)  // 置顶操作加载状态
const loadingHighlight = ref(false)  // 精华操作加载状态
const videoRefs = ref({})  // 视频元素引用

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
    return `<p>${t('postDetail.renderError')}</p>`
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

// 跳转到社区主页
const goToCommunity = () => {
  if (post.value?.community_id) {
    router.push(`/community/${post.value.community_id}`)
  }
}


// 切换视频播放/暂停
const toggleVideoPlay = (event) => {
  const container = event.currentTarget
  const video = container.querySelector('video')
  const overlay = container.querySelector('.video-overlay')
  
  if (video.paused) {
    video.play()
    overlay.style.opacity = '0'
  } else {
    video.pause()
    overlay.style.opacity = '1'
  }
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
    t('postDetail.confirmDelete'),
    t('postDetail.confirmDeleteTitle'),
    {
      confirmButtonText: t('postDetail.confirmDeleteBtn'),
      cancelButtonText: t('common.cancel'),
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
      ElMessage.success(t('postDetail.deleteSuccess'))
      router.push('/')
    } catch (error) {
      ElMessage.error(t('postDetail.deleteFailed'))
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
      ElMessage.success(newState ? t('postDetail.pinSuccess') : t('postDetail.unpinSuccess'))
    }
  } catch (error) {
    console.error('置顶操作失败:', error)
    ElMessage.error(t('postDetail.operationFailed'))
  } finally {
    loadingPin.value = false
  }
}

// 处理版主操作下拉菜单命令
const handleModeratorCommand = async (command) => {
  if (command === 'pin') {
    await handleTogglePin()
  } else if (command === 'highlight') {
    await handleToggleHighlight()
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
      ElMessage.success(newState ? t('postDetail.highlightSuccess') : t('postDetail.unhighlightSuccess'))
    }
  } catch (error) {
    console.error('精华操作失败:', error)
    ElMessage.error(t('postDetail.operationFailed'))
  } finally {
    loadingHighlight.value = false
  }
}

// 加载帖子详情
const loadPost = async () => {
  const postId = parseInt(route.params.id)
  if (isNaN(postId)) {
    loading.value = false
    return
  }

  loading.value = true
  try {
    const [postResponse, myCommunitiesResponse] = await Promise.all([
      client.GET('/v1/posts/{post_id}', {
        params: { path: { post_id: postId } }
      }),
      userStore.isLoggedIn
        ? client.GET('/v1/memberships/my-communities')
        : Promise.resolve({ data: null })
    ])

    if (postResponse.data) {
      post.value = postResponse.data

      if (myCommunitiesResponse.data) {
        const found = myCommunitiesResponse.data.find(c => c.id === post.value.community_id)
        if (found) membership.value = { role: found.role }
      }

      console.log('[PostDetail] 加载成功')
      console.log('[attachments]', post.value.attachments)
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
  background: #fafafa;
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
  gap: 6px;
  margin-bottom: 12px;
  font-size: 13px;
  flex-wrap: wrap;
}

.community-icon {
  font-size: 18px;
}

.community-name {
  font-weight: 500;
  color: #0079d3;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s;
}

.community-name:hover {
  color: #0056a3;
  text-decoration: underline;
}

.separator {
  color: #ccc;
}

.post-time {
  color: #999;
}

/* 作者专属操作按钮 */
.author-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.author-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #666;
  transition: all 0.2s;
}

.author-action-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.author-action-btn.delete {
  color: #d32f2f;
}

.author-action-btn.delete:hover {
  background: #fff0f0;
  color: #c62828;
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
  gap: 3px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  line-height: 1;
}

.pinned-badge {
  background: #fff0ed;
  color: #d63031;
  border: 1px solid #ffd9d9;
}

.highlighted-badge {
  background: #fffbe6;
  color: #d48806;
  border: 1px solid #ffe58f;
}

.post-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.4;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #0079d3;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 500;
}

.author-avatar-img {
  background: transparent;
  object-fit: cover;
  border: 1px solid #e8e8e8;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.author-info:hover .author-avatar-img {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  padding: 12px 0;
  margin: 20px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.actions-left {
  display: flex;
  align-items: center;
  gap: 4px;
}

.actions-left .action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: none;
  background: transparent;
  border-radius: 16px;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
  color: #888;
  font-size: 13px;
  font-weight: 500;
  height: 32px;
  box-sizing: border-box;
}

.actions-left .action-btn:hover {
  background: #f5f5f5;
  color: #555;
}

/* 右侧操作区 */
.actions-right {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
}

/* 版主操作下拉框按钮 */
.moderator-dropdown-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  border: 0.5px solid #e0e0e0;
  cursor: pointer;
  transition: all 0.2s;
  background: transparent;
  color: var(--color-text-secondary, #888);
}

.moderator-dropdown-btn:hover:not(:disabled) {
  background: #f5f5f5;
  color: #555;
}

.moderator-dropdown-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 下拉菜单样式 */
:deep(.el-dropdown-menu) {
  padding: 4px;
}

:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  font-size: 13px;
  color: #555;
}

:deep(.el-dropdown-menu__item:hover) {
  background: #f5f5f5;
  color: #333;
}

:deep(.el-dropdown-menu__item .lucide) {
  flex-shrink: 0;
}

.content-body {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
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

/* 附件区域 - 优化样式 */
.post-attachments-section {
  margin-top: 24px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #eee;
}

.post-attachments-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
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
  border: 1px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.image-attachment img:hover {
  transform: scale(1.01);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

/* 图片附件说明文字（图注） */
.image-attachment .attachment-info {
  margin-top: 8px;
  padding: 0 4px;
}

.image-attachment .file-name {
  font-size: 13px;
  color: #888;
}

.image-attachment .file-size {
  font-size: 12px;
  color: #aaa;
}

.video-attachment {
  flex-direction: column;
  align-items: flex-start;
}

.video-container {
  position: relative;
  width: 100%;
  cursor: pointer;
}

.video-player {
  width: 100%;
  max-height: 400px;
  border-radius: 8px;
  display: block;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  transition: opacity 0.3s;
}

.video-overlay:hover {
  background: rgba(0, 0, 0, 0.4);
}

.play-button {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s, background 0.2s;
}

.play-button:hover {
  transform: scale(1.1);
  background: #fff;
}

.play-button :deep(svg) {
  margin-left: 4px; /* Play 图标向右偏移一点，使三角形居中 */
}

.file-attachment {
  padding: 14px;
  background: white;
  border-radius: 10px;
  border: 1px solid #eee;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.file-icon {
  font-size: 28px;
  flex-shrink: 0;
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
  background: #ffffff;
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
