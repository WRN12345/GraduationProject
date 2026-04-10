<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import PostCard from '../PostCard.vue'
import UserListItem from './UserListItem.vue'
import CommentListItem from './CommentListItem.vue'
import { Search } from 'lucide-vue-next'

const props = defineProps({
  tab: {
    type: String,
    default: 'posts'
  },
  posts: {
    type: Array,
    default: () => []
  },
  users: {
    type: Array,
    default: () => []
  },
  comments: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  query: {
    type: String,
    default: ''
  },
  hasMore: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['load-more'])

const router = useRouter()

// 是否有结果
const hasResults = computed(() => {
  return props.posts.length > 0 || props.users.length > 0 || props.comments.length > 0
})

// 显示帖子
const showPosts = computed(() => {
  return props.tab === 'posts'
})

// 显示用户
const showUsers = computed(() => {
  return props.tab === 'users'
})

// 显示评论
const showComments = computed(() => {
  return props.tab === 'comments'
})

// 加载更多
const handleLoadMore = () => {
  emit('load-more')
}

// 跳转到帖子详情
const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}
</script>

<template>
  <div class="search-results-list">
    <!-- 加载状态 -->
    <div v-if="loading && !hasResults" class="loading-state">
      <div class="spinner"></div>
      <p>搜索中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error && !hasResults" class="error-state">
      <Search :size="48" />
      <h3>搜索出错</h3>
      <p>{{ error }}</p>
      <button class="retry-btn" @click="$emit('retry')">重试</button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!hasResults && !loading" class="empty-state">
      <Search :size="48" />
      <h3>没有找到相关内容</h3>
      <p>试试其他关键词或切换搜索类型</p>
    </div>

    <!-- 搜索结果 -->
    <div v-else class="results-container">
      <!-- 帖子部分 -->
      <div v-if="showPosts && posts.length > 0" class="result-section">
        <PostCard
          v-for="post in posts"
          :key="`post-${post.id}`"
          :post="post"
          @click="goToPost(post.id)"
        />
      </div>

      <!-- 用户部分 -->
      <div v-if="showUsers && users.length > 0" class="result-section">
        <UserListItem
          v-for="user in users"
          :key="`user-${user.id}`"
          :user="user"
        />
      </div>

      <!-- 评论部分 -->
      <div v-if="showComments && comments.length > 0" class="result-section">
        <CommentListItem
          v-for="comment in comments"
          :key="`comment-${comment.id}`"
          :comment="comment"
          :query="query"
        />
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore" class="load-more-container">
        <button
          class="load-more-btn"
          @click="handleLoadMore"
          :disabled="loading"
        >
          <span v-if="loading">加载中...</span>
          <span v-else>加载更多</span>
        </button>
      </div>

      <div v-else-if="hasResults" class="no-more">
        <p>已经到底了</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-results-list {
  min-height: 400px;
  width: 100%;
}

.results-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

/* 统一各类型结果section的宽度，与帖子列表保持一致 */
.result-section {
  width: 100%;
}

/* 加载状态 */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #878a8c;
  gap: 16px;
  padding: 40px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #edeff1;
  border-top-color: #0079d3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p,
.error-state p,
.empty-state p {
  margin: 0;
  font-size: 14px;
}

.error-state h3,
.empty-state h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1c1c1c;
}

.retry-btn {
  padding: 10px 24px;
  background: #0079d3;
  color: var(--text-inverse);
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
  margin-top: 8px;
}

.retry-btn:hover {
  background: #0066b3;
}

/* 加载更多 */
.load-more-container,
.no-more {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}

.load-more-btn {
  padding: 12px 32px;
  background: var(--bg-card);
  border: 1px solid #0079d3;
  border-radius: 24px;
  color: #0079d3;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.load-more-btn:hover:not(:disabled) {
  background: #0079d3;
  color: var(--text-inverse);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.no-more p {
  color: #878a8c;
  font-size: 14px;
  margin: 0;
}

/* 响应式 */
@media (max-width: 639px) {
  .loading-state,
  .error-state,
  .empty-state {
    padding: 32px 16px;
    min-height: 300px;
  }

  .error-state h3,
  .empty-state h3 {
    font-size: 16px;
  }

  .loading-state p,
  .error-state p,
  .empty-state p {
    font-size: 13px;
  }

  .retry-btn {
    padding: 8px 20px;
    font-size: 13px;
  }
}
</style>
