<script setup>
import { ElMessageBox } from 'element-plus'
import { Crown, Shield, ShieldOff, Ban, Unlock } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

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
  const memberName = props.member.nickname || props.member.username
  ElMessageBox.confirm(
    t('memberActions.confirmTransferMessage', { name: memberName }),
    t('memberActions.confirmTransfer'),
    {
      confirmButtonText: t('memberActions.confirmTransferBtn'),
      cancelButtonText: t('communityForm.cancel'),
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
  const memberName = props.member.nickname || props.member.username
  ElMessageBox.confirm(
    t('memberActions.confirmPromoteMessage', { name: memberName }),
    t('memberActions.confirmPromote'),
    {
      confirmButtonText: t('memberActions.confirmPromoteBtn'),
      cancelButtonText: t('communityForm.cancel'),
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
  const memberName = props.member.nickname || props.member.username
  ElMessageBox.confirm(
    t('memberActions.confirmDemoteMessage', { name: memberName }),
    t('memberActions.confirmDemote'),
    {
      confirmButtonText: t('memberActions.confirmDemoteBtn'),
      cancelButtonText: t('communityForm.cancel'),
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
  const memberName = props.member.nickname || props.member.username
  ElMessageBox.confirm(
    t('memberActions.confirmBanMessage', { name: memberName }),
    t('memberActions.confirmBan'),
    {
      confirmButtonText: t('memberActions.confirmBanBtn'),
      cancelButtonText: t('communityForm.cancel'),
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
  const memberName = props.member.nickname || props.member.username
  ElMessageBox.confirm(
    t('memberActions.confirmUnbanMessage', { name: memberName }),
    t('memberActions.confirmUnban'),
    {
      confirmButtonText: t('memberActions.confirmUnbanBtn'),
      cancelButtonText: t('communityForm.cancel'),
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
      {{ t('memberActions.transferOwnership') }}
    </el-button>

    <!-- 提升为管理员（仅 owner 对 member 可见） -->
    <el-button
      v-if="permissions.canPromote"
      text
      size="small"
      @click="handlePromote"
    >
      <Shield :size="14" />
      {{ t('memberActions.promoteToAdmin') }}
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
      {{ t('memberActions.demoteToMember') }}
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
      {{ t('memberActions.ban') }}
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
      {{ t('memberActions.unban') }}
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
