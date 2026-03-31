<template>
  <div class="my-communities">
    <header class="page-header">
      <h1>{{ t('myCommunities.title') }}</h1>
      <button class="btn-create" @click="goToCreateCommunity">
        <Plus :size="20" />
        <span>{{ t('myCommunities.createCommunity') }}</span>
      </button>
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('common.loading') }}</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadCommunities">{{ t('main.retry') }}</button>
    </div>

    <!-- 空状态 -->
    <div v-else-if="communities.length === 0" class="empty-state">
      <Users :size="64" />
      <h3>{{ t('myCommunities.noCommunities') }}</h3>
      <p>{{ t('myCommunities.exploreTip') }}</p>
      <button class="btn-explore" @click="goToExplore">
        <Search :size="18" />
        <span>{{ t('myCommunities.exploreCommunities') }}</span>
      </button>
    </div>

    <!-- 社区网格 -->
    <div v-else class="communities-grid">
      <div
        v-for="community in communities"
        :key="community.id"
        class="community-card"
        @click="goToDetail(community.id)"
      >
        <div class="card-header">
          <span class="community-icon">👾</span>
          <span class="community-name">{{ community.name }}</span>
          <div class="header-actions">
            <span class="role-badge" :class="getRoleClass(community.role)">
              {{ getRoleDisplay(community.role) }}
            </span>
            <button
              v-if="canManageMembers(community.role)"
              class="btn-members"
              @click="goToMembers($event, community.id)"
            >
              <Settings :size="14" />
              {{ t('myCommunities.memberManagement') }}
            </button>
          </div>
        </div>

        <p class="description">{{ community.description || t('common.noDescription') }}</p>

        <div class="stats">
          <span class="stat">
            <Users :size="14" />
            {{ community.member_count }} {{ t('common.members') }}
          </span>
          <span class="stat">
            <FileText :size="14" />
            {{ community.post_count }} {{ t('common.posts') }}
          </span>
        </div>

        <div class="footer">
          <span class="join-time">{{ t('common.joinedAt', { time: formatTime(community.joined_at) }) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Users, Plus, Search, FileText, Settings } from 'lucide-vue-next'
import { client } from '@/api/client'
import { useFormatTime } from '@/composables/useFormatTime'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { formatTime } = useFormatTime()
const { t } = useI18n()

// 状态
const communities = ref([])
const loading = ref(false)
const error = ref(null)

// 加载社区列表
const loadCommunities = async () => {
  loading.value = true
  error.value = null

  try {
    const response = await client.GET('/v1/memberships/my-communities', {
      params: {
        query: {
          skip: 0,
          limit: 50
        }
      }
    })

    if (response.data) {
      communities.value = response.data
      console.log('[我的社区] 加载成功，数量:', communities.value.length)
    }
  } catch (err) {
    console.error('[我的社区] 加载失败:', err)
    error.value = t('myCommunities.loadError')
  } finally {
    loading.value = false
  }
}

// 获取角色显示文本
const getRoleDisplay = (role) => {
  const roleKeyMap = {
    2: 'communityInfoCard.owner',
    1: 'communityInfoCard.admin',
    0: 'communityInfoCard.member'
  }
  return t(roleKeyMap[role] || 'communityInfoCard.member')
}

// 获取角色样式类
const getRoleClass = (role) => {
  const classMap = {
    2: 'owner',
    1: 'admin',
    0: 'member'
  }
  return classMap[role] || 'member'
}


// 跳转到社区详情
const goToDetail = (communityId) => {
  router.push(`/community/${communityId}`)
}

// 跳转到创建社区
const goToCreateCommunity = () => {
  router.push('/create-community')
}

// 跳转到探索页面（暂时跳转到主页）
const goToExplore = () => {
  router.push('/')
}

// 跳转到成员管理页
const goToMembers = (event, communityId) => {
  event.stopPropagation() // 阻止卡片点击事件
  router.push(`/community/${communityId}/members`)
}

// 检查是否为管理员或版主
const canManageMembers = (role) => {
  return role === 2 || role === 1 // owner 或 admin
}

// 初始化
onMounted(() => {
  console.log('[我的社区] 组件挂载')
  loadCommunities()
})
</script>

<style scoped>
.my-communities {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1c1c1c;
  margin: 0;
}

.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #0079d3;
  color: #fff;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-create:hover {
  background: #0066b3;
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

.retry-btn,
.btn-explore {
  padding: 10px 24px;
  background: #0079d3;
  color: #fff;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.retry-btn:hover,
.btn-explore:hover {
  background: #0066b3;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1c1c1c;
  margin: 0;
}

.empty-state p {
  font-size: 14px;
  color: #878a8c;
  margin: 0;
}

/* 社区网格 */
.communities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.community-card {
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.community-card:hover {
  border-color: #0079d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.community-icon {
  font-size: 24px;
}

.community-name {
  font-size: 16px;
  font-weight: 600;
  color: #1c1c1c;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-members {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #0079d3;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-members:hover {
  background: #0066b3;
}

.role-badge {
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
}

.role-badge.owner {
  background: #e6f2ff;
  color: #0079d3;
}

.role-badge.admin {
  background: #fff3e6;
  color: #ff4500;
}

.role-badge.member {
  background: #f6f7f8;
  color: #878a8c;
}

.description {
  color: #1c1c1c;
  font-size: 14px;
  line-height: 1.5;
  margin: 0 0 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 42px;
}

.stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  color: #878a8c;
  font-size: 13px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
}

.footer {
  padding-top: 12px;
  border-top: 1px solid #edeff1;
}

.join-time {
  color: #878a8c;
  font-size: 12px;
}

/* 响应式 */
@media (max-width: 639px) {
  .my-communities {
    padding: 16px 8px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .page-header h1 {
    font-size: 24px;
  }

  .communities-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .community-card {
    padding: 16px;
  }
}

@media (min-width: 640px) and (max-width: 959px) {
  .communities-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
