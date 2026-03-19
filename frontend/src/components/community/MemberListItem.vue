<script setup>
import { useRouter } from 'vue-router'
import { Calendar, Award } from 'lucide-vue-next'
import MemberActions from './MemberActions.vue'

const router = useRouter()

const props = defineProps({
  member: {
    type: Object,
    required: true
  },
  permissions: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['transfer', 'promote', 'demote', 'ban', 'unban'])

// 点击用户卡片跳转到用户主页
const handleClick = () => {
  router.push(`/user/${props.member.username}`)
}

// 获取头像文字（首字母）
const getAvatarText = () => {
  const name = props.member?.username || 'U'
  return name.charAt(0).toUpperCase()
}

// 头像加载失败处理
const handleAvatarError = (event) => {
  event.target.style.display = 'none'
  const textElement = event.target.nextElementSibling
  if (textElement) {
    textElement.style.display = 'flex'
  }
}

// 获取角色名称
const getRoleName = (role) => {
  const map = { 2: '群主', 1: '管理员', 0: '成员', '-1': '已封禁' }
  return map[role] || '成员'
}

// 获取角色样式类
const getRoleClass = (role) => {
  const map = { 2: 'owner', 1: 'admin', 0: 'member', '-1': 'banned' }
  return map[role] || 'member'
}

// 格式化时间
const formatTime = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}
</script>

<template>
  <div class="member-list-item" @click="handleClick">
    <!-- 用户头像 -->
    <div class="user-avatar">
      <img
        v-if="member.avatar"
        :src="member.avatar"
        class="avatar-img"
        @error="handleAvatarError"
      />
      <div class="avatar-text">{{ getAvatarText() }}</div>
    </div>

    <!-- 用户信息 -->
    <div class="member-info">
      <div class="user-name-section">
        <span class="user-display-name">{{ member.nickname || member.username }}</span>
        <span v-if="member.nickname" class="user-username">@{{ member.username }}</span>
        <span class="role-badge" :class="getRoleClass(member.role)">
          {{ getRoleName(member.role) }}
        </span>
      </div>

      <!-- 用户统计 -->
      <div class="member-stats">
        <span class="stat-item">
          <Calendar :size="14" />
          加入于 {{ formatTime(member.joined_at) }}
        </span>
        <span class="stat-item">
          <Award :size="14" />
          {{ member.karma || 0 }} karma
        </span>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="member-actions" @click.stop>
      <MemberActions
        :permissions="permissions"
        :member="member"
        @transfer="emit('transfer')"
        @promote="emit('promote')"
        @demote="emit('demote')"
        @ban="emit('ban')"
        @unban="emit('unban')"
      />
    </div>
  </div>
</template>

<style scoped>
.member-list-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.member-list-item:hover {
  border-color: #0079d3;
  box-shadow: 0 2px 8px rgba(0, 121, 211, 0.1);
}

/* 用户头像 */
.user-avatar {
  position: relative;
  width: 48px;
  height: 48px;
  flex-shrink: 0;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  background: #ddd;
}

.avatar-text {
  display: none;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #0079d3;
  color: #fff;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
}

/* 用户信息 */
.member-info {
  flex: 1;
  min-width: 0;
}

.user-name-section {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.user-display-name {
  font-size: 15px;
  font-weight: 600;
  color: #1c1c1c;
}

.user-username {
  font-size: 13px;
  color: #878a8c;
}

.role-badge {
  padding: 2px 8px;
  border-radius: 6px;
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

.role-badge.banned {
  background: #fee;
  color: #cc0000;
}

/* 用户统计 */
.member-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #878a8c;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 操作按钮区域 */
.member-actions {
  flex-shrink: 0;
}

/* 响应式 */
@media (max-width: 639px) {
  .member-list-item {
    padding: 12px;
    gap: 12px;
  }

  .user-avatar {
    width: 40px;
    height: 40px;
  }

  .avatar-text {
    font-size: 16px;
  }

  .user-display-name {
    font-size: 14px;
  }

  .user-username {
    font-size: 12px;
  }

  .member-stats {
    gap: 12px;
  }
}
</style>
