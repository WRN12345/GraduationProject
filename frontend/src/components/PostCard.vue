<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { MessageCircle, Share2, Pin, Star } from 'lucide-vue-next'
import VoteButtons from './VoteButtons.vue'
import BookmarkButton from './BookmarkButton.vue'

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click'])

const router = useRouter()

// 计算帖子的特殊状态class
const postCardClasses = computed(() => {
  const classes = []
  if (props.post.is_pinned) {
    classes.push('is-pinned')
  }
  if (props.post.is_highlighted) {
    classes.push('is-highlighted')
  }
  return classes
})

// 点击帖子
const handleClick = () => {
  emit('click', props.post.id)
}

// 点击帖子内容区域
const handleContentClick = () => {
  router.push(`/post/${props.post.id}`)
}

// 获取头像文字（首字母）
const getAvatarText = () => {
  const name = props.post?.author?.username || 'U'
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
  const diff = (now - date) / 1000 // 秒

  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  if (diff < 604800) return `${Math.floor(diff / 86400)} 天前`

  return date.toLocaleDateString('zh-CN')
}

// 更新投票状态
const updateVote = (state) => {
  props.post.upvotes = state.upvotes
  props.post.downvotes = state.downvotes
  props.post.user_vote = state.userVote
  props.post.score = state.upvotes - state.downvotes
}

// 更新收藏状态
const updateBookmark = (bookmarked, count) => {
  props.post.bookmarked = bookmarked
  props.post.bookmark_count = count
}

// 获取图片附件
const imageAttachments = computed(() => {
  return props.post.attachments?.filter(a => a.attachment_type === 'image') || []
})

// 获取视频附件
const videoAttachments = computed(() => {
  return props.post.attachments?.filter(a => a.attachment_type === 'video') || []
})

// 是否有附件
const hasAttachments = computed(() => {
  return imageAttachments.value.length > 0 || videoAttachments.value.length > 0
})
</script>

<template>
  <div class="post-card" :class="postCardClasses" @click="handleContentClick">
    <!-- 帖子内容 -->
    <div class="post-content">
      <div class="post-header">
        <div class="author-avatar">
          <img
            v-if="post.author?.avatar"
            :src="post.author.avatar"
            class="avatar-img"
            @error="handleAvatarError"
          />
          <div v-else class="avatar-text">{{ getAvatarText() }}</div>
        </div>
        <span class="community-icon">👾</span>
        <span class="community-name" @click.stop="router.push(`/community/${post.community?.id}`)">
          {{ post.community?.name || '未知社区' }}
        </span>
        <span class="meta-info">· 由 {{ post.author?.username || '匿名用户' }} 发布 · {{ formatTime(post.created_at) }}</span>
      </div>

      <div class="post-title-row">
        <!-- 状态标识 -->
        <div class="status-badges">
          <span v-if="post.is_pinned" class="status-badge pinned-badge" title="置顶帖子">
            <Pin :size="14" />
            <span>置顶</span>
          </span>
          <span v-if="post.is_highlighted" class="status-badge highlighted-badge" title="精华帖子">
            <Star :size="14" />
            <span>精华</span>
          </span>
        </div>
        <h3 class="post-title">{{ post.title }}</h3>
      </div>

      <!-- 内容预览 -->
      <div class="post-preview" v-if="post.content">
        {{ post.content.substring(0, 200) }}{{ post.content.length > 200 ? '...' : '' }}
      </div>

      <!-- 附件预览区域 -->
      <div class="attachments-preview" v-if="hasAttachments">
        <!-- 图片附件 -->
        <div class="attachment-grid images-grid" v-if="imageAttachments.length > 0">
          <div
            v-for="(img, index) in imageAttachments.slice(0, 4)"
            :key="img.id"
            class="attachment-item image-item"
            :class="{ 'more-item': index === 3 && imageAttachments.length > 4 }"
          >
            <img :src="img.file_url" :alt="img.file_name" />
            <div v-if="index === 3 && imageAttachments.length > 4" class="more-overlay">
              +{{ imageAttachments.length - 4 }}
            </div>
          </div>
        </div>

        <!-- 视频附件 -->
        <div class="attachment-grid videos-grid" v-if="videoAttachments.length > 0">
          <div
            v-for="video in videoAttachments"
            :key="video.id"
            class="attachment-item video-item"
          >
            <video :src="video.file_url" :controls="false" preload="metadata"></video>
            <div class="play-icon">▶</div>
          </div>
        </div>
      </div>

      <!-- 底部操作区 -->
      <div class="post-footer" @click.stop>
        <!-- 左侧：点赞点踩 收藏 -->
        <div class="footer-left">
          <!-- 投票按钮 -->
          <VoteButtons
            :target-type="'post'"
            :target-id="post.id"
            :upvotes="post.upvotes || 0"
            :downvotes="post.downvotes || 0"
            :user-vote="post.user_vote || 0"
            :show-count="true"
            :icon-size="16"
            @vote-change="updateVote"
          />

          <!-- 收藏按钮 -->
          <BookmarkButton
            :post-id="post.id"
            :bookmarked="post.bookmarked || false"
            :count="post.bookmark_count || 0"
            :show-count="true"
            :icon-size="16"
            @bookmark-change="updateBookmark"
          />
        </div>

        <!-- 右侧：评论 转发 -->
        <div class="footer-right">
          <button class="action-btn" title="评论" @click="handleContentClick">
            <MessageCircle :size="18" />
            <span>{{ post.comment_count || 0 }}</span>
          </button>
          <button class="action-btn" title="转发">
            <Share2 :size="18" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-card {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.post-card:hover {
  border-color: #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 置顶帖子 - 左侧 3px 红色色条 */
.post-card.is-pinned {
  border-left: 3px solid #ff4500;
}

/* 精华帖子 - 左侧 3px 暖黄色色条 */
.post-card.is-highlighted {
  border-left: 3px solid #e6a700;
}

/* 置顶+精华 - 保留红色 */
.post-card.is-pinned.is-highlighted {
  border-left: 3px solid #ff4500;
}

/* 状态标识 */
.post-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.status-badges {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
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

.post-content {
  padding: 12px 16px;
}

.post-header {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.meta-info {
  color: #999;
}

.meta-info .separator {
  margin: 0 4px;
  color: #ccc;
}

.author-avatar {
  position: relative;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  background: transparent;
  border: 1px solid #e8e8e8;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.author-avatar:hover .avatar-img {
  transform: scale(1.08);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.avatar-text {
  display: flex;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #0079d3;
  color: #fff;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
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
  font-size: 16px;
  margin: 0 0 10px 0;
  font-weight: 500;
  color: #1a1a1a;
  line-height: 1.5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.post-preview {
  color: #444;
  font-size: 14px;
  line-height: 1.7;
  margin-bottom: 12px;
}

/* 附件预览区域 */
.attachments-preview {
  margin-bottom: 12px;
}

.attachment-grid {
  display: grid;
  gap: 8px;
}

.images-grid {
  grid-template-columns: repeat(4, 1fr);
  max-height: 300px;
}

.videos-grid {
  grid-template-columns: repeat(2, 1fr);
}

.attachment-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
}

.image-item {
  aspect-ratio: 16 / 9;
  cursor: pointer;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.image-item:hover img {
  transform: scale(1.02);
}

.image-item.more-item::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.more-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 20px;
  font-weight: 600;
}

.video-item {
  aspect-ratio: 16 / 9;
  cursor: pointer;
}

.video-item video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.play-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 48px;
  height: 48px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  transition: all 0.2s ease;
}

.video-item:hover .play-icon {
  background: rgba(0, 0, 0, 0.8);
  transform: translate(-50%, -50%) scale(1.1);
}

/* 响应式优化 */
@media (max-width: 639px) {
  .images-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .videos-grid {
    grid-template-columns: 1fr;
  }

  .play-icon {
    width: 40px;
    height: 40px;
    font-size: 14px;
  }
}

/* 底部操作区 */
.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
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
  background: transparent;
  border: none;
  padding: 6px 10px;
  color: #888;
  font-size: 12px;
  font-weight: 500;
  border-radius: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f5f5f5;
  color: #555;
}

/* 响应式优化 */
@media (max-width: 639px) {
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

  .post-footer {
    flex-wrap: wrap;
    gap: 4px;
  }

  .footer-left,
  .footer-right {
    gap: 2px;
  }

  .action-btn {
    padding: 6px 8px;
    font-size: 12px;
  }
}
</style>
