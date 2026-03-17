<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from 'lucide-vue-next'
import { useSearch } from '@/composables/useSearch'
import SearchTabs from '@/components/search/SearchTabs.vue'
import SearchResultsList from '@/components/search/SearchResultsList.vue'

const route = useRoute()
const router = useRouter()

// 从 URL 获取搜索参数
const searchQuery = ref(route.query.q || '')
const activeTab = ref(route.query.tab || 'posts')

// 使用搜索 composable
const {
  resultPosts,
  resultUsers,
  resultComments,
  totalResults,
  searchLoading,
  searchError,
  searchByTab,
  loadMore,
  hasMore,
  currentQuery
} = useSearch()

// 计算各类型的数量
const tabCounts = computed(() => ({
  posts: resultPosts.value.length,
  users: resultUsers.value.length,
  comments: resultComments.value.length
}))

// 执行搜索
const performSearch = async () => {
  if (!searchQuery.value || searchQuery.value.trim().length < 1) {
    return
  }

  // 更新 URL 参数
  router.replace({
    path: '/search',
    query: {
      q: searchQuery.value,
      tab: activeTab.value
    }
  })

  // 执行搜索
  await searchByTab(searchQuery.value, activeTab.value, true)
}

// 切换标签
const handleTabChange = async (tab) => {
  activeTab.value = tab

  // 更新 URL 参数
  router.replace({
    path: '/search',
    query: {
      q: searchQuery.value,
      tab: tab
    }
  })

  // 执行搜索
  await searchByTab(searchQuery.value, tab, true)
}

// 加载更多
const handleLoadMore = () => {
  loadMore()
}

// 重试
const handleRetry = () => {
  performSearch()
}

// 监听路由参数变化
watch(() => route.query, (newQuery) => {
  if (newQuery.q !== searchQuery.value) {
    searchQuery.value = newQuery.q || ''
    activeTab.value = newQuery.tab || 'all'

    if (searchQuery.value) {
      performSearch()
    }
  }
}, { immediate: false })

// 初始化搜索
onMounted(() => {
  if (searchQuery.value) {
    performSearch()
  }
})
</script>

<template>
  <div class="search-results-page">
    <!-- 搜索标签 -->
    <SearchTabs
      v-model="activeTab"
      :counts="tabCounts"
      @update:modelValue="handleTabChange"
    />

    <!-- 搜索结果列表 -->
    <SearchResultsList
      :tab="activeTab"
      :posts="resultPosts"
      :users="resultUsers"
      :comments="resultComments"
      :loading="searchLoading"
      :error="searchError"
      :query="currentQuery"
      :has-more="hasMore"
      @load-more="handleLoadMore"
      @retry="handleRetry"
    />

    <!-- 无搜索关键词提示 -->
    <div v-if="!searchQuery" class="no-query-state">
      <Search :size="64" />
      <h3>请输入搜索关键词</h3>
      <p>在顶部搜索框中输入内容，然后按 Enter 搜索</p>
    </div>
  </div>
</template>

<style scoped>
.search-results-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 20px 20px 20px;
}

/* 页面头部 */
.page-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #edeff1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 700;
  color: #1c1c1c;
}

.title-icon {
  color: #0079d3;
}

.search-query {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 14px;
}

.query-label {
  color: #878a8c;
}

.query-text {
  color: #0079d3;
  font-weight: 600;
}

.query-count {
  padding: 4px 12px;
  background: #f6f7f8;
  color: #878a8c;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

/* 无搜索关键词状态 */
.no-query-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #878a8c;
  gap: 16px;
  padding: 40px 20px;
}

.no-query-state h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1c1c1c;
}

.no-query-state p {
  margin: 0;
  font-size: 14px;
  color: #878a8c;
}

/* 响应式 */
@media (max-width: 639px) {
  .search-results-page {
    padding: 0 16px 16px 16px;
  }

  .page-header {
    margin-bottom: 20px;
    padding-bottom: 12px;
  }

  .page-title {
    font-size: 20px;
  }

  .title-icon {
    width: 20px;
    height: 20px;
  }

  .search-query {
    font-size: 13px;
  }

  .query-count {
    padding: 3px 10px;
    font-size: 11px;
  }

  .no-query-state {
    padding: 32px 16px;
    min-height: 300px;
  }

  .no-query-state h3 {
    font-size: 18px;
  }

  .no-query-state p {
    font-size: 13px;
  }
}
</style>
