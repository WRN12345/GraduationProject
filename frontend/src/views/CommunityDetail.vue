<template>
  <div class="community-detail">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="router.push('/my-communities')">返回我的社区</button>
    </div>

    <!-- 社区内容 -->
    <div v-else-if="community">
      <!-- 顶部：社区信息卡片 -->
      <section class="community-info-section">
        <CommunityInfoCard
          :community="community"
          :role="membership?.role"
          @leave="handleLeave"
          @join="handleJoin"
        />
      </section>

      <!-- 下方：帖子列表 -->
      <section class="posts-section">
        <div class="posts-header">
          <div class="posts-title">
            <h2>社区帖子</h2>
            <span class="post-count">({{ community.post_count || 0 }})</span>
          </div>
          <!-- 成员管理按钮（仅 owner/admin 可见） -->
          <router-link
            v-if="membership?.role === 2 || membership?.role === 1"
            :to="`/community/${communityId}/members`"
            class="members-link"
          >
            <Users :size="16" />
            成员管理
          </router-link>
        </div>
        <PostList
          :community-id="communityId"
          :empty-title="emptyTitle"
          :empty-message="emptyMessage"
        />
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { client } from '@/api/client'
import { Users } from 'lucide-vue-next'
import CommunityInfoCard from '@/components/community/CommunityInfoCard.vue'
import PostList from '@/components/PostList.vue'

const route = useRoute()
const router = useRouter()

const communityId = parseInt(route.params.id)  // 使用数字 ID
const community = ref(null)
const membership = ref(null)
const loading = ref(true)
const error = ref(null)

// 空状态文案
const emptyTitle = computed(() => {
  return `「${community.value?.name || ''}」还没有帖子`
})

const emptyMessage = computed(() => {
  if (membership.value?.role === 2) {
    return '作为版主，快来发布第一篇帖子吧！'
  }
  return '成为第一个发帖的人吧！'
})

// 加载社区详情和用户角色
const loadData = async () => {
  loading.value = true
  error.value = null

  try {
    // 通过 ID 获取社区详情
    const response = await client.GET('/v1/communities/id/{community_id}', {
      params: {
        path: { community_id: communityId }
      }
    })

    if (response.data) {
      community.value = response.data
    } else {
      error.value = '社区不存在'
      loading.value = false
      return
    }

    // 检查用户是否是该社区的成员
    const myCommunitiesResponse = await client.GET('/v1/memberships/my-communities')
    if (myCommunitiesResponse.data) {
      const found = myCommunitiesResponse.data.find(c => c.id === communityId)
      if (found) {
        membership.value = { role: found.role }
      } else {
        // 用户未加入该社区
        membership.value = null
      }
    }
  } catch (err) {
    console.error('[社区详情] 加载失败:', err)
    if (err.response?.status === 404) {
      error.value = '社区不存在'
    } else {
      error.value = '加载失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

// 退出社区后返回列表页
const handleLeave = () => {
  router.push('/my-communities')
}

// 用户加入社区后更新状态
const handleJoin = (data) => {
  membership.value = { role: data.role }
}

// 初始化
onMounted(() => {
  console.log('[社区详情] 组件挂载，communityId:', communityId)
  loadData()
})
</script>

<style scoped>
.community-detail {
  max-width: 980px;
  margin: 0 auto;
  padding: 24px 16px;
}

/* 加载状态 */
.loading-state,
.error-state {
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

.retry-btn {
  padding: 10px 24px;
  background: #0079d3;
  color: #fff;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #0066b3;
}

/* 社区信息区域 */
.community-info-section {
  margin-bottom: 24px;
}

/* 帖子列表区域 */
.posts-section {
  /* PostList 组件自带样式 */
}

.posts-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.posts-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.posts-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1c1c1c;
  margin: 0;
}

.post-count {
  color: #878a8c;
  font-size: 16px;
}

.members-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #0079d3;
  color: #fff;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.2s;
}

.members-link:hover {
  background: #0066b3;
}

/* 响应式 */
@media (max-width: 639px) {
  .community-detail {
    padding: 16px 8px;
  }

  .community-info-section {
    margin-bottom: 16px;
  }

  .posts-header h2 {
    font-size: 18px;
  }
}
</style>
