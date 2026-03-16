<script setup lang="ts">
import { useRouter } from 'vue-router'
import { TrendingUp, Award, MessageSquare, Users } from 'lucide-vue-next'
import type { HotPost } from '@/composables/useTrending'

defineProps({
  posts: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()

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

// 跳转到帖子详情
const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}
</script>

<template>
  <div class="hot-posts-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="posts.length === 0" class="empty-state">
      <p>暂无热门帖子</p>
    </div>

    <!-- 列表内容 -->
    <div v-else class="posts-list">
      <div
        v-for="(post, index) in posts"
        :key="post.id"
        class="hot-post-item"
        @click="goToPost(post.id)"
      >
        <!-- 排名 -->
        <span class="rank" :class="{ 'top-three': index < 3 }">
          <Award v-if="index === 0" :size="20" class="medal gold" />
          <Award v-else-if="index === 1" :size="20" class="medal silver" />
          <Award v-else-if="index === 2" :size="20" class="medal bronze" />
          <span v-else class="number">{{ index + 1 }}</span>
        </span>

        <!-- 帖子信息 -->
        <div class="post-info">
          <h3 class="post-title">{{ post.title }}</h3>
          <div class="post-meta">
            <Users :size="12" class="meta-icon" />
            <span class="community-name">{{ post.community_name }}</span>
            <span class="separator">·</span>
            <span class="author">{{ post.author_username }}</span>
            <span class="separator">·</span>
            <span class="time">{{ formatTime(post.created_at) }}</span>
          </div>
        </div>

        <!-- 热度分数 -->
        <div class="hot-score">
          <TrendingUp :size="14" class="fire-icon" />
          <span class="score">{{ post.hot_rank.toFixed(1) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hot-posts-list {
  width: 100%;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #878a8c;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #edeff1;
  border-top-color: #0079d3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  margin-top: 12px;
  font-size: 14px;
}

/* 空状态 */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #878a8c;
  font-size: 14px;
}

/* 列表 */
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hot-post-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background-color: #ffffff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hot-post-item:hover {
  background-color: #f6f7f8;
  border-color: #d3d6da;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* 排名 */
.rank {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  font-weight: 700;
  font-size: 14px;
}

.rank .medal {
  display: flex;
  align-items: center;
  justify-content: center;
}

.rank .medal.gold {
  color: #ffd700;
}

.rank .medal.silver {
  color: #c0c0c0;
}

.rank .medal.bronze {
  color: #cd7f32;
}

.rank .number {
  color: #878a8c;
}

.rank.top-three .number {
  color: #1c1c1c;
}

/* 帖子信息 */
.post-info {
  flex: 1;
  min-width: 0;
}

.post-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #878a8c;
  flex-wrap: wrap;
}

.meta-icon {
  flex-shrink: 0;
}

.community-name {
  color: #0079d3;
  font-weight: 500;
}

.separator {
  color: #878a8c;
}

/* 热度分数 */
.hot-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  padding: 4px 8px;
  background: linear-gradient(135deg, #FFB3BA 0%, #FFDFBa 100%);
  border-radius: 6px;
  color: #ffffff;
}

.fire-icon {
  font-size: 14px;
  line-height: 1;
  color: #1c1c1c;
}

.score {
  font-size: 12px;
  font-weight: 700;
  line-height: 1.2;
  color: #1c1c1c;
}

/* 响应式 */
@media (max-width: 639px) {
  .hot-post-item {
    padding: 10px;
    gap: 8px;
  }

  .post-title {
    font-size: 13px;
  }

  .post-meta {
    font-size: 11px;
  }

  .hot-score {
    min-width: 40px;
    color: #1c1c1c;
  }

  .fire-icon {
    font-size: 12px;
  }

  .score {
    font-size: 11px;
  }
}
</style>
