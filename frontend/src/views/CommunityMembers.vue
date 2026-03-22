<template>
  <div class="community-members">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <div>
          <h1>{{ communityName }} - 成员管理</h1>
          <p class="subtitle">共 {{ sortedMemberList.length }} 位成员</p>
        </div>
      </div>

      <!-- 退出社区按钮（非 owner） -->
      <el-button
        v-if="!isOwner"
        type="danger"
        plain
        @click="handleLeave"
      >
        <LogOut :size="16" />
        退出社区
      </el-button>
    </header>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button class="retry-btn" @click="loadMembers">重试</button>
    </div>

    <!-- 成员列表 -->
    <div v-else class="members-list">
      <!-- 按角色分组显示 -->
      <section v-for="roleGroup in groupedMembers" :key="roleGroup.role" class="role-group">
        <div class="group-header">
          <h2>{{ roleGroup.roleName }}</h2>
          <span class="count">{{ roleGroup.members.length }}</span>
        </div>

        <div class="members-grid">
          <MemberListItem
            v-for="member in roleGroup.members"
            :key="member.id"
            :member="member"
            :permissions="getMemberPermissions(member)"
            @transfer="handleTransfer(member.user_id)"
            @promote="handlePromote(member.user_id)"
            @demote="handleDemote(member.user_id)"
            @ban="handleBan(member.user_id)"
            @unban="handleUnban(member.user_id)"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { client } from '@/api/client'
import { ElMessage } from 'element-plus'
import { LogOut } from 'lucide-vue-next'
import MemberListItem from '@/components/community/MemberListItem.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const communityId = parseInt(route.params.id)
const communityName = ref('社区')
const rawMemberList = ref([])
const membership = ref(null)
const loading = ref(false)
const error = ref(null)

// 角色优先级映射
const ROLE_PRIORITY = {
  2: 0,  // OWNER - 最高优先级
  1: 1,  // ADMIN
  0: 2,  // MEMBER
  '-1': 3 // BANNED - 最低优先级
}

// 排序后的成员列表
const sortedMemberList = computed(() => {
  if (!rawMemberList.value) return []
  return [...rawMemberList.value].sort((a, b) => {
    const priorityA = ROLE_PRIORITY[a.role] ?? 2
    const priorityB = ROLE_PRIORITY[b.role] ?? 2
    if (priorityA !== priorityB) {
      return priorityA - priorityB
    }
    // 同角色按加入时间排序
    const timeA = new Date(a.joined_at || 0).getTime()
    const timeB = new Date(b.joined_at || 0).getTime()
    return timeA - timeB
  })
})

// 当前用户角色
const currentUserRole = computed(() => membership.value?.role ?? 0)
const isOwner = computed(() => currentUserRole.value === 2)
const isAdmin = computed(() => currentUserRole.value === 1)
const isModerator = computed(() => isOwner.value || isAdmin.value)

// 按角色分组
const groupedMembers = computed(() => {
  const groups = {
    2: { role: 2, roleName: '版主', members: [] },
    1: { role: 1, roleName: '管理员', members: [] },
    0: { role: 0, roleName: '成员', members: [] },
    '-1': { role: -1, roleName: '已封禁', members: [] }
  }

  sortedMemberList.value.forEach(member => {
    const role = member.role
    if (groups[role]) {
      groups[role].members.push(member)
    }
  })

  // 按固定顺序返回：版主 → 管理员 → 成员 → 已封禁
  const order = [2, 1, 0, -1]
  return order.map(role => groups[role]).filter(g => g.members.length > 0)
})

// 对某个成员的权限检查
const getMemberPermissions = (member) => {
  const isSelf = userStore.userId === member.user_id
  return {
    canTransfer: isOwner.value && member.role === 1 && !isSelf,
    canPromote: isOwner.value && member.role === 0,
    canDemote: isOwner.value && member.role === 1,
    canBan: isModerator.value && member.role === 0 && !isSelf,
    canUnban: isModerator.value && member.role === -1
  }
}

// 加载成员列表
const loadMembers = async () => {
  loading.value = true
  error.value = null

  try {
    // 获取成员列表
    const response = await client.GET('/v1/memberships/communities/{community_id}/members', {
      params: {
        path: { community_id: communityId },
        query: { skip: 0, limit: 100 }
      }
    })

    if (response.data) {
      rawMemberList.value = response.data

      // 从成员列表中找到当前用户的角色
      const myMembership = response.data.find(m => m.user_id === userStore.userId)
      if (myMembership) {
        membership.value = { role: myMembership.role }
      }

      // 获取社区名称（从 my-communities 中获取）
      const myCommunitiesResponse = await client.GET('/v1/memberships/my-communities')
      if (myCommunitiesResponse.data) {
        const community = myCommunitiesResponse.data.find(c => c.id === communityId)
        if (community) {
          communityName.value = community.name
        }
      }
    }
  } catch (err) {
    console.error('[成员管理] 加载失败:', err)
    error.value = '加载成员列表失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 封禁用户
const handleBan = async (memberId) => {
  try {
    await client.POST('/v1/memberships/communities/{community_id}/members/{user_id}/ban', {
      params: {
        path: { community_id: communityId, user_id: memberId }
      }
    })
    ElMessage.success('已封禁用户')
    await loadMembers()
  } catch (err) {
    console.error('[成员管理] 封禁失败:', err)
    ElMessage.error(err.response?.data?.detail || '封禁失败')
  }
}

// 解封用户
const handleUnban = async (memberId) => {
  try {
    await client.POST('/v1/memberships/communities/{community_id}/members/{user_id}/unban', {
      params: {
        path: { community_id: communityId, user_id: memberId }
      }
    })
    ElMessage.success('已解封用户')
    await loadMembers()
  } catch (err) {
    console.error('[成员管理] 解封失败:', err)
    ElMessage.error(err.response?.data?.detail || '解封失败')
  }
}

// 提升为管理员
const handlePromote = async (memberId) => {
  try {
    await client.POST('/v1/memberships/communities/{community_id}/members/{user_id}/promote', {
      params: {
        path: { community_id: communityId, user_id: memberId }
      }
    })
    ElMessage.success('已提升为管理员')
    await loadMembers()
  } catch (err) {
    console.error('[成员管理] 提升失败:', err)
    ElMessage.error(err.response?.data?.detail || '提升失败')
  }
}

// 降级为成员
const handleDemote = async (memberId) => {
  try {
    await client.POST('/v1/memberships/communities/{community_id}/members/{user_id}/demote', {
      params: {
        path: { community_id: communityId, user_id: memberId }
      }
    })
    ElMessage.success('已降级为成员')
    await loadMembers()
  } catch (err) {
    console.error('[成员管理] 降级失败:', err)
    ElMessage.error(err.response?.data?.detail || '降级失败')
  }
}

// 转让版主
const handleTransfer = async (memberId) => {
  try {
    await client.POST('/v1/memberships/communities/{community_id}/transfer-ownership', {
      params: {
        path: { community_id: communityId }
      },
      body: { user_id: memberId }
    })
    ElMessage.success('已转让版主')
    router.push('/my-communities')
  } catch (err) {
    console.error('[成员管理] 转让失败:', err)
    ElMessage.error(err.response?.data?.detail || '转让失败')
  }
}

// 退出社区
const handleLeave = async () => {
  if (isOwner.value) {
    ElMessage.warning('版主需要先转让版主才能退出社区')
    return
  }

  try {
    await client.POST('/v1/memberships/communities/{community_id}/leave', {
      params: {
        path: { community_id: communityId }
      }
    })
    ElMessage.success('已退出社区')
    router.push('/my-communities')
  } catch (err) {
    console.error('[成员管理] 退出失败:', err)
    ElMessage.error(err.response?.data?.detail || '退出失败')
  }
}

// 初始化
onMounted(() => {
  loadMembers()
})
</script>

<style scoped>
.community-members {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 16px;
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 16px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-header h1 {
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

/* 加载和错误状态 */
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

/* 角色分组 */
.role-group {
  margin-bottom: 40px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #edeff1;
}

.group-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1c1c1c;
  margin: 0;
}

.count {
  padding: 2px 10px;
  background: #f6f7f8;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: #878a8c;
}

/* 成员网格 */
.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

/* 响应式 */
@media (max-width: 639px) {
  .community-members {
    padding: 16px 8px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .members-grid {
    grid-template-columns: 1fr;
  }

  .page-header h1 {
    font-size: 20px;
  }
}
</style>
