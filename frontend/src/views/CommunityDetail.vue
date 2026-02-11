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
          :role="membership.role"
          @leave="handleLeave"
        />
      </section>

      <!-- 下方：帖子列表 -->
      <section class="posts-section">
        <div class="posts-header">
          <h2>社区帖子</h2>
          <span class="post-count">({{ community.post_count || 0 }})</span>
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
import CommunityInfoCard from '@/components/community/CommunityInfoCard.vue'
import PostList from '@/components/PostList.vue'

const route = useRoute()
const router = useRouter()

const communityId = parseInt(route.params.id)
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
    return '作为群主，快来发布第一篇帖子吧！'
  }
  return '成为第一个发帖的人吧！'
})

// 加载社区详情和用户角色
const loadData = async () => {
  loading.value = true
  error.value = null

  try {
    // 获取社区详情
    const communityResponse = await client.GET('/v1/communities/{name}', {
      params: {
        path: { name: communityId }  // 这个可能需要改为 id 查询
      }
    })

    // 上面的路径可能不对，我们需要从 my-communities 获取的数据中找到
    // 或者我们需要一个新的 API 端点来获取社区详情

    // 暂时使用 my-communities 的数据
    const myCommunitiesResponse = await client.GET('/v1/memberships/my-communities')

    if (myCommunitiesResponse.data) {
      const found = myCommunitiesResponse.data.find(c => c.id === communityId)
      if (found) {
        community.value = found
        membership.value = { role: found.role }
      } else {
        // 用户不是该社区成员
        error.value = '你不是该社区的成员'
      }
    }
  } catch (err) {
    console.error('[社区详情] 加载失败:', err)
    error.value = '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 退出社区后返回列表页
const handleLeave = () => {
  router.push('/my-communities')
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
  gap: 8px;
  margin-bottom: 16px;
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
