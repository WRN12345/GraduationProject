<script setup lang="ts">
import { useRouter } from 'vue-router'
import { TrendingUp, Award, Star, FileText, MessageCircle } from 'lucide-vue-next'
import type { HotUser } from '@/composables/useTrending'

defineProps({
  users: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()

// 跳转到用户资料（如果有的话）
const goToUser = (username) => {
  router.push(`/user/${username}`)
}

// 格式化数字
const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

// 获取用户显示名称
const getDisplayName = (user) => {
  return user.nickname || user.username
}
</script>

<template>
  <div class="hot-users-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="users.length === 0" class="empty-state">
      <p>暂无活跃用户</p>
    </div>

    <!-- 列表内容 -->
    <div v-else class="users-list">
      <div
        v-for="(user, index) in users"
        :key="user.id"
        class="hot-user-item"
        @click="goToUser(user.username)"
      >
        <!-- 排名 -->
        <span class="rank" :class="{ 'top-three': index < 3 }">
          <Award v-if="index === 0" :size="20" class="medal gold" />
          <Award v-else-if="index === 1" :size="20" class="medal silver" />
          <Award v-else-if="index === 2" :size="20" class="medal bronze" />
          <span v-else class="number">{{ index + 1 }}</span>
        </span>

        <!-- 用户头像 -->
        <div class="user-avatar">
          <img
            v-if="user.avatar"
            :src="user.avatar"
            :alt="user.username"
            class="avatar-image"
          />
          <div v-else class="avatar-placeholder">
            {{ user.username[0].toUpperCase() }}
          </div>
        </div>

        <!-- 用户信息 -->
        <div class="user-info">
          <h3 class="user-username">{{ getDisplayName(user) }}</h3>
          <div class="user-meta">
            <span class="meta-item">
              <Star :size="11" class="icon" />
              <span>{{ formatNumber(user.karma) }}</span>
            </span>
            <span class="separator">·</span>
            <span class="meta-item">
              <FileText :size="11" class="icon" />
              <span>{{ formatNumber(user.post_count) }}</span>
            </span>
            <span class="separator">·</span>
            <span class="meta-item">
              <MessageCircle :size="11" class="icon" />
              <span>{{ formatNumber(user.comment_count) }}</span>
            </span>
          </div>
        </div>

        <!-- 热度分数 -->
        <div class="hot-score">
          <TrendingUp :size="14" class="fire-icon" />
          <span class="score">{{ user.hot_rank.toFixed(1) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hot-users-list {
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
.users-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hot-user-item {
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

.hot-user-item:hover {
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

/* 用户头像 */
.user-avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
}

/* 用户信息 */
.user-info {
  flex: 1;
  min-width: 0;
}

.user-username {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #878a8c;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 2px;
}

.meta-item .icon {
  font-size: 11px;
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
  background: linear-gradient(135deg, #E0BBE4 0%, #D4F0F0 100%);
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
  .hot-user-item {
    padding: 10px;
    gap: 8px;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
  }

  .avatar-placeholder {
    font-size: 16px;
  }

  .user-username {
    font-size: 13px;
  }

  .user-meta {
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
