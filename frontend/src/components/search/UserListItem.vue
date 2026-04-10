<script setup>
import { useRouter } from 'vue-router'
import { Award, MessageCircle, FileText } from 'lucide-vue-next'

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})

const router = useRouter()

// 点击用户卡片
const handleClick = () => {
  router.push(`/user/${props.user.username}`)
}

// 获取头像文字（首字母）
const getAvatarText = () => {
  const name = props.user?.username || 'U'
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
</script>

<template>
  <div class="user-list-item" @click="handleClick">
    <!-- 用户头像 -->
    <div class="user-avatar">
      <img
        v-if="user.avatar"
        :src="user.avatar"
        class="avatar-img"
        @error="handleAvatarError"
      />
      <div class="avatar-text">{{ getAvatarText() }}</div>
    </div>

    <!-- 用户信息 -->
    <div class="user-info">
      <div class="user-name-section">
        <span class="user-display-name">{{ user.nickname || user.username }}</span>
        <span v-if="user.nickname" class="user-username">@{{ user.username }}</span>
      </div>

      <!-- 用户统计 -->
      <div class="user-stats">
        <div class="stat-item">
          <Award :size="14" />
          <span>{{ user.karma || 0 }} karma</span>
        </div>
        <div class="stat-item">
          <FileText :size="14" />
          <span>{{ user.post_count || 0 }} 帖子</span>
        </div>
        <div class="stat-item">
          <MessageCircle :size="14" />
          <span>{{ user.comment_count || 0 }} 评论</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-list-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--bg-card);
  border: 1px solid #edeff1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 12px;
  width: 100%;
  box-sizing: border-box;
}

.user-list-item:hover {
  border-color: #0079d3;
  box-shadow: 0 2px 8px rgba(0, 121, 211, 0.1);
}

/* 用户头像 */
.user-avatar {
  position: relative;
  width: 56px;
  height: 56px;
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
  display: none;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #0079d3;
  color: var(--text-inverse);
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
}

/* 用户信息 */
.user-info {
  flex: 1;
  min-width: 0;
}

.user-name-section {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.user-display-name {
  font-size: 16px;
  font-weight: 600;
  color: #1c1c1c;
}

.user-username {
  font-size: 14px;
  color: #787c7e;
}

/* 用户统计 */
.user-stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #878a8c;
}

.stat-item:first-child {
  color: #ff4500;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 639px) {
  .user-list-item {
    padding: 12px;
    gap: 12px;
    border-radius: 0;
    border-left: none;
    border-right: none;
    margin-bottom: 0;
  }

  .user-avatar {
    width: 48px;
    height: 48px;
  }

  .avatar-text {
    font-size: 18px;
  }

  .user-display-name {
    font-size: 15px;
  }

  .user-username {
    font-size: 13px;
  }

  .user-stats {
    gap: 12px;
  }

  .stat-item {
    font-size: 12px;
  }
}
</style>
