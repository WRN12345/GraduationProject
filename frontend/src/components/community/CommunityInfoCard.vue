<template>
  <div class="community-info-card">
    <div class="community-header">
      <span class="community-icon">👾</span>
      <h2 class="community-name">{{ community.name }}</h2>
      <span v-if="roleDisplay" class="role-badge" :class="roleClass">{{ roleDisplay }}</span>
    </div>

    <p class="description">{{ community.description || t('common.noDescription') }}</p>

    <div class="stats">
      <div class="stat-item">
        <Users :size="16" />
        <span>{{ community.member_count || 0 }} {{ t('common.members') }}</span>
      </div>
      <div class="stat-item">
        <FileText :size="16" />
        <span>{{ community.post_count || 0 }} {{ t('common.posts') }}</span>
      </div>
      <div class="stat-item" v-if="community.created_at">
        <Calendar :size="16" />
        <span>{{ t('common.createdAt', { time: formatTime(community.created_at) }) }}</span>
      </div>
    </div>

    <div class="actions">
      <!-- 未加入社区时显示加入按钮 -->
      <button v-if="!isMember" class="btn-primary" @click="handleJoin">
        <UserPlus :size="16" />
        <span>{{ t('communityInfoCard.joinCommunity') }}</span>
      </button>
      <!-- 已加入社区时显示发帖和退出按钮 -->
      <template v-else>
        <button class="btn-primary" @click="goToCreatePost">
          <Plus :size="16" />
          <span>{{ t('communityInfoCard.createPost') }}</span>
        </button>
        <button class="btn-secondary" @click="handleLeave" v-if="canLeave">
          <LogOut :size="16" />
          <span>{{ t('communityInfoCard.leaveCommunity') }}</span>
        </button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Users, FileText, Calendar, Plus, LogOut, UserPlus } from 'lucide-vue-next'
import { useFormatTime } from '@/composables/useFormatTime'
import { client } from '@/api/client'

const { t } = useI18n()
const { formatTime } = useFormatTime()

const props = defineProps({
  community: {
    type: Object,
    required: true
  },
  role: {
    type: Number,
    default: undefined  // undefined=未加入, 0=成员, 1=管理员, 2=版主
  }
})

const emit = defineEmits(['leave', 'join'])

const router = useRouter()

// 角色显示
const roleDisplay = computed(() => {
  // 未加入社区时不显示标签
  if (props.role === undefined || props.role === null) {
    return ''
  }
  const roleKeyMap = {
    2: 'communityInfoCard.owner',
    1: 'communityInfoCard.admin',
    0: 'communityInfoCard.member'
  }
  return t(roleKeyMap[props.role] || 'communityInfoCard.member')
})

// 角色样式类
const roleClass = computed(() => {
  // 未加入社区时不显示标签
  if (props.role === undefined || props.role === null) {
    return ''
  }
  const classMap = {
    2: 'owner',
    1: 'admin',
    0: 'member'
  }
  return classMap[props.role] || 'member'
})

// 是否已加入社区
const isMember = computed(() => {
  return props.role !== undefined && props.role !== null
})

// 是否可以退出（版主不能直接退出）
const canLeave = computed(() => {
  return props.role !== 2
})

// 跳转到创建帖子页面
const goToCreatePost = () => {
  router.push(`/create-post?community_id=${props.community.id}`)
}

// 退出社区
const handleLeave = async () => {
  if (!confirm(t('communityInfoCard.confirmLeave', { name: props.community.name }))) {
    return
  }

  try {
    const response = await client.POST('/v1/memberships/communities/{community_id}/leave', {
      params: {
        path: { community_id: props.community.id }
      }
    })

    if (response.data) {
      alert(t('communityInfoCard.leftSuccess'))
      emit('leave')
      // 跳转回我的社区页面
      router.push('/my-communities')
    }
  } catch (error) {
    console.error('[CommunityInfoCard] 退出社区失败:', error)
    alert(t('communityInfoCard.leaveFailed', { error: error?.message || t('common.unknownTime') }))
  }
}

// 加入社区
const handleJoin = async () => {
  try {
    const response = await client.POST(`/v1/communities/${props.community.id}/join`)

    if (response.data) {
      alert(t('communityInfoCard.joinSuccess'))
      emit('join', { role: 0 })  // 0 = 普通成员
    }
  } catch (error) {
    console.error('[CommunityInfoCard] 加入社区失败:', error)
    alert(t('communityInfoCard.joinFailed', { error: error?.message || t('common.unknownTime') }))
  }
}
</script>

<style scoped>
.community-info-card {
  background: var(--bg-card);
  border: 1px solid #edeff1;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.community-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.community-icon {
  font-size: 32px;
}

.community-name {
  font-size: 24px;
  font-weight: 700;
  color: #1c1c1c;
  margin: 0;
  flex: 1;
}

.role-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
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
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 20px 0;
}

.stats {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #878a8c;
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 12px;
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #0079d3;
  color: var(--text-inverse);
}

.btn-primary:hover {
  background: #0066b3;
}

.btn-secondary {
  background: #f6f7f8;
  color: #1c1c1c;
}

.btn-secondary:hover {
  background: #edeff1;
}

/* 响应式 */
@media (max-width: 639px) {
  .community-info-card {
    padding: 16px;
  }

  .community-name {
    font-size: 20px;
  }

  .stats {
    gap: 16px;
  }

  .actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
    justify-content: center;
  }
}
</style>
