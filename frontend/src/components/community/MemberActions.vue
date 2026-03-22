<script setup>
import { ElMessageBox } from 'element-plus'
import { Crown, Shield, ShieldOff, Ban, Unlock } from 'lucide-vue-next'

const props = defineProps({
  permissions: {
    type: Object,
    required: true
  },
  member: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['transfer', 'promote', 'demote', 'ban', 'unban'])

// 转让版主
const handleTransfer = () => {
  ElMessageBox.confirm(
    `确定要将版主转让给「${props.member.nickname || props.member.username}」吗？转让后你将成为管理员。`,
    '确认转让版主',
    {
      confirmButtonText: '确认转让',
      cancelButtonText: '取消',
      type: 'warning',
      distinguishCancelAndClose: true
    }
  ).then(() => {
    emit('transfer')
  }).catch(() => {
    // 用户取消
  })
}

// 提升为管理员
const handlePromote = () => {
  ElMessageBox.confirm(
    `确定要将「${props.member.nickname || props.member.username}」提升为管理员吗？`,
    '确认提升',
    {
      confirmButtonText: '确认提升',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    emit('promote')
  }).catch(() => {
    // 用户取消
  })
}

// 降级为成员
const handleDemote = () => {
  ElMessageBox.confirm(
    `确定要将「${props.member.nickname || props.member.username}」降级为普通成员吗？`,
    '确认降级',
    {
      confirmButtonText: '确认降级',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    emit('demote')
  }).catch(() => {
    // 用户取消
  })
}

// 封禁用户
const handleBan = () => {
  ElMessageBox.confirm(
    `确定要封禁「${props.member.nickname || props.member.username}」吗？封禁后将无法访问社区。`,
    '确认封禁',
    {
      confirmButtonText: '确认封禁',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    emit('ban')
  }).catch(() => {
    // 用户取消
  })
}

// 解封用户
const handleUnban = () => {
  ElMessageBox.confirm(
    `确定要解封「${props.member.nickname || props.member.username}」吗？`,
    '确认解封',
    {
      confirmButtonText: '确认解封',
      cancelButtonText: '取消',
      type: 'success'
    }
  ).then(() => {
    emit('unban')
  }).catch(() => {
    // 用户取消
  })
}
</script>

<template>
  <div class="member-actions">
    <!-- 转让版主（仅 owner 对 admin 可见） -->
    <el-button
      v-if="permissions.canTransfer"
      text
      size="small"
      type="primary"
      @click="handleTransfer"
    >
      <Crown :size="14" />
      转让版主
    </el-button>

    <!-- 提升为管理员（仅 owner 对 member 可见） -->
    <el-button
      v-if="permissions.canPromote"
      text
      size="small"
      @click="handlePromote"
    >
      <Shield :size="14" />
      提升管理
    </el-button>

    <!-- 降级为成员（仅 owner 对 admin 可见） -->
    <el-button
      v-if="permissions.canDemote"
      text
      size="small"
      type="warning"
      @click="handleDemote"
    >
      <ShieldOff :size="14" />
      降级成员
    </el-button>

    <!-- 封禁（owner/admin 对 member 可见） -->
    <el-button
      v-if="permissions.canBan"
      text
      size="small"
      type="danger"
      @click="handleBan"
    >
      <Ban :size="14" />
      封禁
    </el-button>

    <!-- 解封（owner/admin 对 banned 可见） -->
    <el-button
      v-if="permissions.canUnban"
      text
      size="small"
      type="success"
      @click="handleUnban"
    >
      <Unlock :size="14" />
      解封
    </el-button>
  </div>
</template>

<style scoped>
.member-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.member-actions :deep(.el-button) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin: 0;
}

/* 响应式 */
@media (max-width: 639px) {
  .member-actions {
    width: 100%;
  }

  .member-actions :deep(.el-button) {
    font-size: 12px;
  }
}
</style>
