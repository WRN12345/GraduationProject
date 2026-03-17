<script setup>
import { useRouter } from 'vue-router'
import { MessageCircle, Share2 } from 'lucide-vue-next'
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
  const textElement = event.target.nextElementSibling
  if (textElement) {
    textElement.style.display = 'flex'
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
</script>

<template>
  <div class="post-card" @click="handleContentClick">
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
          <div class="avatar-text">{{ getAvatarText() }}</div>
        </div>
        <span class="community-icon">👾</span>
        <span class="community-name" @click.stop="router.push(`/community/${post.community?.id}`)">
          {{ post.community?.name || '未知社区' }}
        </span>
        <span class="meta-info">· 由 {{ post.author?.username || '匿名用户' }} 发布 · {{ formatTime(post.created_at) }}</span>
      </div>

      <h3 class="post-title">{{ post.title }}</h3>

      <!-- 内容预览 -->
      <div class="post-preview" v-if="post.content">
        {{ post.content.substring(0, 200) }}{{ post.content.length > 200 ? '...' : '' }}
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
  border: 1px solid #e6e6e6;
}

.avatar-text {
  display: none;
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
