<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { FileText, Flame, Clock } from 'lucide-vue-next'
import { useFormatTime } from '@/composables/useFormatTime'

const { formatTime } = useFormatTime()

const props = defineProps({
  // 搜索建议相关
  posts: {
    type: Array,
    default: () => []
  },
  users: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  query: {
    type: String,
    default: ''
  },
  // 热搜相关
  hotPosts: {
    type: Array,
    default: () => []
  },
  hotUsers: {
    type: Array,
    default: () => []
  },
  hotLoading: {
    type: Boolean,
    default: false
  },
  showHot: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'close'])

const router = useRouter()

// 判断是否显示热搜模式
const isHotMode = computed(() => {
  return props.showHot && !props.query
})

// 选择帖子建议
const selectPost = (post) => {
  emit('select', { type: 'post', item: post })
  // 跳转到帖子详情
  router.push(`/post/${post.id}`)
}

// 选择用户建议（仅在搜索建议模式中使用）
const selectUser = (user) => {
  emit('select', { type: 'user', item: user })
  // 跳转到用户详情
  router.push(`/user/${user.username}`)
}

// 查看全部搜索结果
const viewAllResults = () => {
  if (props.query) {
    emit('close')
    router.push({ path: '/search', query: { q: props.query } })
  }
}


// 获取头像文字（首字母）
const getAvatarText = (user) => {
  const name = user?.username || user?.author_username || 'U'
  return name.charAt(0).toUpperCase()
}
</script>

<template>
  <div class="search-suggestions">
    <!-- 加载状态 -->
    <div v-if="loading || hotLoading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ isHotMode ? '加载热搜...' : '搜索中...' }}</p>
    </div>

    <!-- 热搜模式 -->
    <div v-else-if="isHotMode" class="hot-mode">
      <div class="dropdown-header">
        <Flame :size="14" />
        <span>热门帖子</span>
      </div>

      <!-- 热门帖子 -->
      <div v-if="hotPosts.length > 0" class="hot-posts-list">
        <div v-for="(post, index) in hotPosts.slice(0, 5)" :key="`hot-post-${post.id}`"
             class="hot-post-item" @click="selectPost(post)">
          <div class="post-rank">{{ index + 1 }}</div>
          <FileText :size="18" class="post-icon" />
          <div class="post-info">
            <div class="post-title">{{ post.title }}</div>
            <div class="post-meta">
              <span class="community-name">{{ post.community_name || '未知社区' }}</span>
              <span class="separator">·</span>
              <Clock :size="12" />
              <span class="time">{{ formatTime(post.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="hotPosts.length === 0" class="empty-state">
        <Flame :size="32" />
        <p>暂无热门内容</p>
      </div>
    </div>

    <!-- 搜索建议模式 -->
    <div v-else-if="posts.length > 0 || users.length > 0">
      <!-- 帖子建议 -->
      <div v-if="posts.length > 0" class="suggestion-section">
        <div class="dropdown-header">
          <FileText :size="14" />
          <span>帖子</span>
        </div>
        <div
          v-for="post in posts"
          :key="`post-${post.id}`"
          class="suggestion-item"
          @click="selectPost(post)"
        >
          <FileText :size="18" class="item-icon" />
          <div class="suggestion-content">
            <div class="suggestion-title">{{ post.title }}</div>
            <div class="suggestion-meta">
              <span class="community-name">{{ post.community?.name || '未知社区' }}</span>
              <span class="separator">·</span>
              <span class="time">{{ formatTime(post.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 用户建议 -->
      <div v-if="users.length > 0" class="suggestion-section">
        <div class="dropdown-header">
          <TrendingUp :size="14" />
          <span>用户</span>
        </div>
        <div
          v-for="user in users"
          :key="`user-${user.id}`"
          class="suggestion-item"
          @click="selectUser(user)"
        >
          <div class="user-avatar">
            <img
              v-if="user.avatar"
              :src="user.avatar"
              class="avatar-img"
            />
            <div class="avatar-text">{{ getAvatarText(user) }}</div>
          </div>
          <div class="suggestion-content">
            <div class="suggestion-title">{{ user.nickname || user.username }}</div>
            <div class="suggestion-meta">
              <span class="username">@{{ user.username }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 查看全部 -->
      <div v-if="query" class="view-all" @click="viewAllResults">
        <span>查看 "{{ query }}" 的全部搜索结果</span>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="query && !loading" class="empty-state">
      <p>没有找到相关内容</p>
    </div>
  </div>
</template>

<style scoped>
.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #edeff1;
  border-top: none;
  border-bottom-left-radius: 24px;
  border-bottom-right-radius: 24px;
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
  z-index: 1001;
  max-height: 400px;
  overflow-y: auto;
  padding-bottom: 8px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 20px;
  gap: 12px;
  color: #878a8c;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #edeff1;
  border-top-color: #0079d3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  margin: 0;
  font-size: 14px;
}

/* 热搜模式 */
.hot-mode .dropdown-header {
  color: #ff4500;
}

.dropdown-header {
  padding: 12px 20px 8px;
  font-size: 12px;
  font-weight: 700;
  color: #878a8c;
  display: flex;
  align-items: center;
  gap: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 热门帖子列表 */
.hot-posts-list {
  padding: 4px 0;
}

.hot-post-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  gap: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.hot-post-item:hover {
  background-color: #f6f7f8;
}

/* 排名 */
.post-rank {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #878a8c;
  flex-shrink: 0;
}

.post-icon {
  color: #878a8c;
  flex-shrink: 0;
}

/* 帖子信息 */
.post-info {
  flex: 1;
  min-width: 0;
}

.post-title {
  font-size: 14px;
  font-weight: 500;
  color: #1c1c1c;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #878a8c;
  margin-top: 2px;
}

.community-name {
  color: #0079d3;
  font-weight: 500;
}

.separator {
  color: #d3d3d3;
}

.time {
  color: #878a8c;
}

/* 搜索建议模式 */
.suggestion-section {
  padding: 4px 0;
}

.suggestion-section:not(:last-child) {
  border-bottom: 1px solid #f6f7f8;
}

.suggestion-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  gap: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.suggestion-item:hover {
  background-color: #f6f7f8;
}

.item-icon {
  color: #878a8c;
  flex-shrink: 0;
}

.suggestion-content {
  flex: 1;
  min-width: 0;
}

.suggestion-title {
  font-size: 14px;
  font-weight: 500;
  color: #1c1c1c;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggestion-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #878a8c;
  margin-top: 2px;
}

.username {
  color: #878a8c;
}

/* 用户头像 */
.user-avatar {
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
  display: none;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #0079d3;
  color: #fff;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

/* 查看全部 */
.view-all {
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 600;
  color: #0079d3;
  cursor: pointer;
  transition: background 0.15s;
  text-align: center;
  border-top: 1px solid #edeff1;
  margin-top: 8px;
}

.view-all:hover {
  background-color: #f6f7f8;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 20px;
  gap: 12px;
  color: #878a8c;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 639px) {
  .search-suggestions {
    max-height: 300px;
  }

  .dropdown-header {
    padding: 10px 16px 6px;
  }

  .hot-post-item,
  .suggestion-item {
    padding: 10px 16px;
  }

  .post-title,
  .suggestion-title {
    font-size: 13px;
  }
}
</style>
