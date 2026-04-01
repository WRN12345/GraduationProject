<template>
  <div class="my-bookmarks-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>{{ t('myBookmarks.title') }}</h1>
      <p class="subtitle">{{ t('myBookmarks.count', { count: total }) }}</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && posts.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('common.loading') }}</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="posts.length === 0" class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
      </svg>
      <h3>{{ t('myBookmarks.noBookmarks') }}</h3>
      <p>{{ t('myBookmarks.bookmarkTip') }}</p>
      <el-button type="primary" @click="goToHome">{{ t('myBookmarks.browsePosts') }}</el-button>
    </div>

    <!-- 帖子列表 -->
    <div v-else class="bookmarks-list">
      <!-- 单个帖子卡片 -->
      <div
        v-for="post in posts"
        :key="post.id"
        class="post-card"
        @click="goToPost(post.id)"
      >
        <!-- 社区信息 -->
        <div class="post-header">
          <span class="community-icon">👾</span>
          <span class="community-name">{{ post.community?.name || t('main.unknownCommunity') }}</span>
          <span class="meta-info">
            · {{ t('main.postedBy', { user: post.author?.username || t('common.anonymousUser') }) }}
            · {{ formatTime(post.created_at) }}
          </span>
        </div>

        <!-- 标题 -->
        <h3 class="post-title">{{ post.title }}</h3>

        <!-- 内容预览 -->
        <div class="post-preview" v-if="post.content">
          {{ stripHtml(post.content).substring(0, 200) }}...
        </div>

        <!-- 底部操作区 -->
        <div class="post-footer"@click.stop>
          <VoteButtons
            :post-id="post.id"
            :user-vote="post.user_vote"
            :upvotes="post.upvotes"
            :downvotes="post.downvotes"
            @vote-change="handleVoteChange"
          />

          <div class="footer-right">
            <BookmarkButton
              :post-id="post.id"
              :bookmarked="post.bookmarked"
              :count="post.bookmark_count"
              size="small"
              show-count
            />
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore && !loading" class="load-more">
        <el-button @click="loadMore" :loading="loadingMore">
          {{ t('main.loadMore') }}
        </el-button>
      </div>

      <div v-if="loading && posts.length > 0" class="loading-more">
        <div class="spinner"></div>
        <p>{{ t('common.loading') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { client } from '@/api/client'
import VoteButtons from '@/components/VoteButtons.vue'
import BookmarkButton from '@/components/BookmarkButton.vue'
import { ElMessage } from 'element-plus'
import { useFormatTime } from '@/composables/useFormatTime'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { formatTime } = useFormatTime()
const { t } = useI18n()

// 响应式数据
const posts = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(20)
const hasMore = ref(false)
const loading = ref(false)
const loadingMore = ref(false)


// 去除 HTML 标签
const stripHtml = (html) => {
  const tmp = document.createElement('div')
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ''
}

// 获取收藏列表
const fetchBookmarks = async () => {
  loading.value = true
  try {
    const response = await client.GET('/v1/bookmarks/my-posts', {
      params: {
        query: {
          skip: skip.value,
          limit: limit.value
        }
      }
    })

    posts.value = response.data.items
    total.value = response.data.total
    hasMore.value = response.data.has_more
  } catch (error) {
    console.error('fetch bookmarks failed:', error)
    ElMessage.error(t('myBookmarks.fetchFailed'))
  } finally {
    loading.value = false
  }
}

// 加载更多
const loadMore = async () => {
  loadingMore.value = true
  try {
    skip.value += limit.value

    const response = await client.GET('/v1/bookmarks/my-posts', {
      params: {
        query: {
          skip: skip.value,
          limit: limit.value
        }
      }
    })

    posts.value.push(...response.data.items)
    hasMore.value = response.data.has_more
  } catch (error) {
    console.error('load more bookmarks failed:', error)
    ElMessage.error(t('myBookmarks.loadMoreFailed'))
    skip.value -= limit.value // 回退 skip
  } finally {
    loadingMore.value = false
  }
}

// 跳转到帖子详情
const goToPost = (postId) => {
  router.push(`/post/${postId}`)
}

// 跳转到首页
const goToHome = () => {
  router.push('/')
}

// 处理投票变化
const handleVoteChange = (data) => {
  const post = posts.value.find(p => p.id === data.postId)
  if (post) {
    post.user_vote = data.vote
    post.upvotes = data.upvotes
    post.downvotes = data.downvotes
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchBookmarks()
})
</script>

<style scoped>
.my-bookmarks-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1c1c1c;
}

.subtitle {
  color: #7c7c7c;
  font-size: 16px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #7c7c7c;
}

.empty-state svg {
  margin-bottom: 20px;
  color: #ffd700;
}

.empty-state h3 {
  font-size: 20px;
  margin-bottom: 8px;
}

.bookmarks-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-card {
  background: var(--bg-card);
  border: 1px solid #edf1f5;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.post-card:hover {
  border-color: #0079d3;
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

.community-name {
  font-weight: 600;
  color: #0079d3;
}

.post-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1c1c1c;
}

.post-preview {
  font-size: 14px;
  color: #1c1c1c;
  line-height: 1.5;
  margin-bottom: 12px;
  color: #333;
}

.post-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.footer-right {
  display: flex;
  gap: 12px;
}

.load-more, .loading-more {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 12px;
  color: #7c7c7c;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #edf1f5;
  border-top-color: #0079d3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
