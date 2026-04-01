<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTrending } from '@/composables/useTrending'
import HotPostsList from '@/components/trending/HotPostsList.vue'
import HotCommunitiesList from '@/components/trending/HotCommunitiesList.vue'
import HotUsersList from '@/components/trending/HotUsersList.vue'
import { RotateCw, TrendingUp, FileText, Users, User } from 'lucide-vue-next'

const { t } = useI18n()

// 使用热门内容 composable
const { hotPosts, hotCommunities, hotUsers, loading, error, refreshTrending } = useTrending({
  limit: 10,
  autoFetch: true
})

// Tab 状态
const activeTab = ref('posts')

const tabs = [
  { id: 'posts', label: t('trending.hotPosts'), icon: FileText },
  { id: 'communities', label: t('trending.hotCommunities'), icon: Users },
  { id: 'users', label: t('trending.activeUsers'), icon: User }
]

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
    <!-- 页面头部：Tab 胶囊按钮 + 刷新按钮 -->
    <div class="page-header">
      <!-- 左侧：胶囊按钮 Tab -->
      <div class="tab-container">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-button"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <component :is="tab.icon" :size="14" />
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- 右侧：刷新按钮 -->
      <button
        class="refresh-button"
        @click="handleRefresh"
        :disabled="loading || isRefreshing"
        :class="{ loading: loading || isRefreshing }"
      >
        <RotateCw :size="14" :class="{ spinning: isRefreshing }" />
        <span>{{ t('trending.refresh') }}</span>
      </button>
    </div>

    <!-- 错误状态 -->
    <div v-if="error && !hotPosts.length && !hotCommunities.length && !hotUsers.length" class="error-state">
      <div class="error-content">
        <p class="error-message">{{ error }}</p>
        <button class="retry-button" @click="handleRefresh">
          {{ t('main.retry') }}
        </button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div v-else class="content">
      <!-- 热门帖子 -->
      <div v-show="activeTab === 'posts'" class="tab-content">
        <HotPostsList :posts="hotPosts" :loading="loading" />
      </div>

      <!-- 热门社区 -->
      <div v-show="activeTab === 'communities'" class="tab-content">
        <HotCommunitiesList :communities="hotCommunities" :loading="loading" />
      </div>

      <!-- 活跃用户 -->
      <div v-show="activeTab === 'users'" class="tab-content">
        <HotUsersList :users="hotUsers" :loading="loading" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.trending-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 20px;
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #edeff1;
}

/* Tab 胶囊按钮 */
.tab-container {
  display: flex;
  gap: 4px;
  background-color: #f6f7f8;
  padding: 4px;
  border-radius: 24px;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: transparent;
  border: none;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  color: #878a8c;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-button:hover {
  color: #1c1c1c;
  background-color: #edeff1;
}

.tab-button.active {
  background-color: var(--bg-card);
  color: #1c1c1c;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  font-weight: 600;
}

/* 刷新按钮 */
.refresh-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background-color: #0079d3;
  color: var(--text-inverse);
  border: none;
  border-radius: 20px;
  font-size: 13px;
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
  background-color: var(--bg-card);
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
  color: var(--text-inverse);
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
  background-color: var(--bg-card);
  border: 1px solid #edeff1;
  border-radius: 8px;
  padding: 16px;
}

.tab-content {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 响应式 */
@media (max-width: 639px) {
  .trending-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .tab-container {
    justify-content: center;
  }

  .tab-button {
    padding: 8px 12px;
    font-size: 12px;
  }

  .tab-button span {
    display: none;
  }

  .refresh-button {
    align-self: flex-end;
    padding: 6px 12px;
    font-size: 12px;
  }

  .content {
    padding: 12px;
  }
}
</style>
