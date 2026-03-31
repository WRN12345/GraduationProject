<template>
  <div class="community-manage-container">
    
    <!-- 左右布局 -->
    <div class="content-layout">
      <!-- 左侧：创建表单 -->
      <div class="left-panel">
        <div class="form-section">
          <CommunityForm
            @submit="handleCommunityCreated"
          />
        </div>
      </div>

      <!-- 右侧：社区列表 -->
      <div class="right-panel">
        <div class="communities-section">
          <div class="section-header">
            <h2 class="section-title">
              {{ t('communityManage.myCommunities') }}
              <span class="count">({{ communities.length }})</span>
            </h2>
            <button class="refresh-btn" @click="loadCommunities" :disabled="loading">
              <RefreshCw :size="16" :class="{ spinning: loading }" />
            </button>
          </div>

          <div v-if="loading && communities.length === 0" class="loading-state">
            <div class="spinner"></div>
            <p>{{ t('common.loading') }}</p>
          </div>

          <div v-else-if="communities.length === 0" class="empty-state">
            <Users :size="48" />
            <p>{{ t('communityManage.noCommunities') }}</p>
            <p class="hint">{{ t('communityManage.createFirst') }}</p>
          </div>

          <div v-else class="communities-list">
            <div
              v-for="community in communities"
              :key="community.id"
              class="community-card"
            >
              <div class="community-icon">👾</div>
              <div class="community-info">
                <div class="community-name">{{ community.name }}</div>
                <div class="community-description">{{ community.description }}</div>
                <div class="community-meta">
                  <span class="member-count">
                    <Users :size="14" />
                    {{ formatCount(community.member_count) }}
                  </span>
                  <span class="create-time">
                    {{ formatTime(community.created_at) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  Users,
  RefreshCw
} from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { client } from '@/api/client'
import CommunityForm from '@/components/community/CommunityForm.vue'
import { useFormatTime } from '@/composables/useFormatTime'

const { formatTime } = useFormatTime()
const { t } = useI18n()

const communities = ref([])
const loading = ref(false)

// 格式化数字
const formatCount = (count) => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + 'w'
  } else if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'k'
  }
  return count.toString()
}


// 加载社区列表
const loadCommunities = async () => {
  loading.value = true
  try {
    const response = await client.GET('/v1/communities/', {
      params: {
        query: {
          skip: 0,
          limit: 100
        }
      }
    })
    if (response.data) {
      communities.value = response.data
      console.log('[社区管理] 加载成功，数量:', communities.value.length)
    }
  } catch (error) {
    console.error('[社区管理] 加载失败:', error)
  } finally {
    loading.value = false
  }
}

// 处理社区创建成功
const handleCommunityCreated = (community) => {
  console.log('[社区管理] 创建成功:', community)
  // 重新加载列表
  loadCommunities()
  // 滚动到列表顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  loadCommunities()
})
</script>

<style scoped>
.community-manage-container {
  min-height: calc(100vh - 56px);
  padding: 24px 16px;
  background: #f6f7f8;
}

.manage-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header-content {
  flex: 1;
}

.title {
  font-size: 24px;
  font-weight: 700;
  color: #1c1c1c;
  margin: 0;
}

.subtitle {
  font-size: 14px;
  color: #878a8c;
  margin: 4px 0 0 0;
}

/* 左右布局 */
.content-layout {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

.left-panel {
  width: 480px;
  flex-shrink: 0;
}

.right-panel {
  flex: 1;
  min-width: 0;
}

.communities-section {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1c1c1c;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.count {
  font-size: 14px;
  color: #878a8c;
  font-weight: normal;
}

.refresh-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: #f6f7f8;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: #edeff1;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: #878a8c;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #edeff1;
  border-top-color: #0079d3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

.empty-state {
  gap: 12px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.hint {
  font-size: 12px;
  color: #878a8c;
}

.communities-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.community-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f6f7f8;
  border: 2px solid transparent;
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
}

.community-card:hover {
  border-color: #0079d3;
  background: #fff;
}

.community-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.community-info {
  flex: 1;
  min-width: 0;
}

.community-name {
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
  margin-bottom: 2px;
}

.community-description {
  font-size: 12px;
  color: #878a8c;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.community-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #878a8c;
  margin-top: 4px;
}

.member-count {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 左侧表单区域 */
.form-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
}

/* 响应式 */
@media (max-width: 1023px) {
  .content-layout {
    flex-direction: column;
  }

  .left-panel {
    width: 100%;
    order: -1; /* 表单在移动端显示在上方 */
  }

  .right-panel {
    width: 100%;
  }
}

@media (max-width: 639px) {
  .community-manage-container {
    padding: 16px 8px;
  }

  .manage-header {
    flex-wrap: wrap;
  }

  .title {
    font-size: 20px;
  }

  .subtitle {
    display: none;
  }

  .communities-section,
  .form-section {
    padding: 16px;
  }
}
</style>
