<script setup>
import { ref } from 'vue'
import { useTrending } from '@/composables/useTrending'
import HotPostsList from '@/components/trending/HotPostsList.vue'
import HotCommunitiesList from '@/components/trending/HotCommunitiesList.vue'
import HotUsersList from '@/components/trending/HotUsersList.vue'
import { RotateCw, TrendingUp } from 'lucide-vue-next'

// 使用热门内容 composable
const { hotPosts, hotCommunities, hotUsers, loading, error, refreshTrending } = useTrending({
  limit: 10,
  autoFetch: true
})

// 刷新处理
const isRefreshing = ref(false)
const handleRefresh = async () => {
  isRefreshing.value = true
  await refreshTrending()
  isRefreshing.value = false
}
</script>

<template>
  <div class="trending-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <TrendingUp :size="28" class="title-icon" />
        热门内容
      </h1>
      <button
        class="refresh-button"
        @click="handleRefresh"
        :disabled="loading || isRefreshing"
        :class="{ loading: loading || isRefreshing }"
      >
        <RotateCw :size="16" :class="{ spinning: isRefreshing }" />
        <span>刷新</span>
      </button>
    </div>

    <!-- 错误状态 -->
    <div v-if="error && !hotPosts.length && !hotCommunities.length && !hotUsers.length" class="error-state">
      <div class="error-content">
        <p class="error-message">{{ error }}</p>
        <button class="retry-button" @click="handleRefresh">
          重试
        </button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div v-else class="content">
      <!-- 热门帖子 -->
      <section class="trending-section">
        <div class="section-header">
          <h2 class="section-title">热门帖子</h2>
          <span class="section-count">{{ hotPosts.length }} 条</span>
        </div>
        <HotPostsList :posts="hotPosts" :loading="loading" />
      </section>

      <!-- 热门社区 -->
      <section class="trending-section">
        <div class="section-header">
          <h2 class="section-title">热门社区</h2>
          <span class="section-count">{{ hotCommunities.length }} 个</span>
        </div>
        <HotCommunitiesList :communities="hotCommunities" :loading="loading" />
      </section>

      <!-- 活跃用户 -->
      <section class="trending-section">
        <div class="section-header">
          <h2 class="section-title">活跃用户</h2>
          <span class="section-count">{{ hotUsers.length }} 位</span>
        </div>
        <HotUsersList :users="hotUsers" :loading="loading" />
      </section>
    </div>
  </div>
</template>

<style scoped>
.trending-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 20px;
}

/* 页面标题 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #edeff1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1c1c1c;
}

.title-icon {
  color: #ff6b35;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: #0079d3;
  color: #ffffff;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-button:hover:not(:disabled) {
  background-color: #0066b3;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 121, 211, 0.3);
}

.refresh-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-button.loading {
  opacity: 0.8;
}

.refresh-button :deep(.spinning) {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 错误状态 */
.error-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background-color: #ffffff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  padding: 40px 20px;
}

.error-content {
  text-align: center;
}

.error-message {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #878a8c;
}

.retry-button {
  padding: 10px 24px;
  background-color: #0079d3;
  color: #ffffff;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background-color: #0066b3;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 121, 211, 0.3);
}

/* 内容区域 */
.content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 区块 */
.trending-section {
  background-color: #ffffff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  padding: 20px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #edeff1;
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1c1c1c;
}

.section-count {
  padding: 4px 12px;
  background-color: #f6f7f8;
  color: #878a8c;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 639px) {
  .trending-page {
    padding: 16px;
  }

  .page-header {
    margin-bottom: 20px;
    padding-bottom: 12px;
  }

  .page-title {
    font-size: 20px;
  }

  .title-icon {
    width: 24px;
    height: 24px;
  }

  .refresh-button {
    padding: 6px 12px;
    font-size: 13px;
  }

  .content {
    gap: 24px;
  }

  .trending-section {
    padding: 16px;
  }

  .section-title {
    font-size: 16px;
  }

  .section-count {
    padding: 3px 10px;
    font-size: 11px;
  }
}
</style>
