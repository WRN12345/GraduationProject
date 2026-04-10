<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { MessageCircle, ArrowRight } from 'lucide-vue-next'
import { marked } from 'marked'
import { useFormatTime } from '@/composables/useFormatTime'

const { formatTime } = useFormatTime()

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  query: {
    type: String,
    default: ''
  }
})

const router = useRouter()

// 头像加载失败标记
const avatarFailed = ref(false)

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

// 点击评论跳转到帖子详情
const handleClick = () => {
  if (props.comment?.post?.id) {
    router.push(`/post/${props.comment.post.id}`)
  }
}

// 检查是否有帖子信息
const hasPost = computed(() => {
  return props.comment?.post && typeof props.comment.post === 'object'
})

// 获取头像文字（首字母）
const getAvatarText = () => {
  const name = props.comment?.author?.username || props.comment?.author?.nickname || 'U'
  return name.charAt(0).toUpperCase()
}

// 检查是否有作者信息
const hasAuthor = computed(() => {
  return props.comment?.author && typeof props.comment.author === 'object'
})

// 头像加载失败处理
const handleAvatarError = () => {
  avatarFailed.value = true
}


// 渲染评论内容（去除 HTML 标签）
const renderContent = (content) => {
  if (!content) return ''

  try {
    // 如果有高亮内容（headline），使用高亮内容
    if (props.comment.headline) {
      return props.comment.headline
    }

    // 否则渲染 markdown 并去除 HTML 标签
    const html = marked(content)
    const text = html.replace(/<[^>]*>/g, '')
    return text.length > 300 ? text.substring(0, 300) + '...' : text
  } catch (error) {
    console.error('[CommentListItem] Markdown 渲染错误:', error)
    return content?.substring(0, 300) || ''
  }
}
</script>

<template>
  <div class="comment-list-item" @click="handleClick">
    <!-- 评论头部 -->
    <div class="comment-header">
      <!-- 作者头像 -->
      <div class="author-avatar">
        <img
          v-if="hasAuthor && comment.author.avatar && !avatarFailed"
          :src="comment.author.avatar"
          class="avatar-img"
          @error="handleAvatarError"
        />
        <div v-else class="avatar-text">{{ getAvatarText() }}</div>
      </div>

      <!-- 作者信息 -->
      <div class="author-info">
        <span class="author-name">
          {{ hasAuthor ? (comment.author.nickname || comment.author.username) : '未知用户' }}
        </span>
        <span v-if="hasAuthor && comment.author.nickname" class="author-username">
          @{{ comment.author.username }}
        </span>
        <span class="dot">·</span>
        <span class="time">{{ formatTime(comment.created_at) }}</span>
      </div>
    </div>

    <!-- 评论内容 -->
    <div class="comment-content">
      <MessageCircle :size="16" class="comment-icon" />
      <div class="content-text" v-html="renderContent(comment.content)"></div>
    </div>

    <!-- 所属帖子 -->
    <div v-if="hasPost" class="comment-post">
      <span class="post-label">来自帖子：</span>
      <span class="post-title">{{ comment.post.title }}</span>
      <ArrowRight :size="14" class="arrow-icon" />
    </div>

    <!-- 评论统计 -->
    <div class="comment-stats">
      <div class="stat-item">
        <span class="stat-label">投票</span>
        <span class="stat-value">{{ (comment.upvotes || 0) - (comment.downvotes || 0) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comment-list-item {
  background: var(--bg-card);
  border: 1px solid #edeff1;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 12px;
}

.comment-list-item:hover {
  border-color: #0079d3;
  box-shadow: 0 2px 8px rgba(0, 121, 211, 0.1);
}

/* 评论头部 */
.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.author-avatar {
  position: relative;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  background: #ddd;
}

.avatar-text {
  display: flex;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #0079d3;
  color: var(--text-inverse);
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  font-size: 13px;
}

.author-name {
  font-weight: 600;
  color: #1c1c1c;
}

.author-username {
  color: #787c7e;
}

.dot {
  color: #878a8c;
}

.time {
  color: #878a8c;
}

/* 评论内容 */
.comment-content {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
  padding: 12px;
  background: #f6f7f8;
  border-radius: 8px;
}

.comment-icon {
  color: #878a8c;
  flex-shrink: 0;
  margin-top: 2px;
}

.content-text {
  flex: 1;
  font-size: 14px;
  line-height: 1.5;
  color: #1c1c1c;
  word-break: break-word;
}

/* 高亮样式 */
.content-text :deep(mark) {
  background: #fff3cd;
  padding: 2px 4px;
  border-radius: 2px;
}

/* 所属帖子 */
.comment-post {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 13px;
}

.post-label {
  color: #878a8c;
  white-space: nowrap;
}

.post-title {
  color: #0079d3;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arrow-icon {
  color: #878a8c;
  flex-shrink: 0;
}

/* 评论统计 */
.comment-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #878a8c;
}

.stat-label {
  color: #878a8c;
}

.stat-value {
  font-weight: 600;
  color: #1c1c1c;
}

/* 响应式 */
@media (max-width: 639px) {
  .comment-list-item {
    padding: 12px;
    border-radius: 0;
    border-left: none;
    border-right: none;
    margin-bottom: 0;
  }

  .comment-content {
    padding: 10px;
  }

  .author-info {
    font-size: 12px;
  }

  .content-text {
    font-size: 13px;
  }

  .comment-post {
    font-size: 12px;
  }

  .stat-item {
    font-size: 12px;
  }
}
</style>
