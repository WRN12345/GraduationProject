<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { getAuditLogs } from '@/api/admin'
import { useFormatTime } from '@/composables/useFormatTime'

const { t } = useI18n()
const { formatTime } = useFormatTime()

const actionTypeFilter = ref('')
const targetTypeFilter = ref('')

const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

// 操作类型选项
const actionTypes = computed(() => [
  { label: t('admin.activity.filterAllTypes'), value: '' },
  { label: 'ADMIN_DELETE_POST', value: 30 },
  { label: 'ADMIN_RESTORE_POST', value: 31 },
  { label: 'ADMIN_HARD_DELETE_POST', value: 32 },
  { label: 'ADMIN_DELETE_COMMENT', value: 33 },
  { label: 'ADMIN_HARD_DELETE_COMMENT', value: 34 },
  { label: 'ADMIN_RESTORE_COMMENT', value: 35 },
  { label: 'BAN_USER', value: 3 },
  { label: 'UNBAN_USER', value: 4 },
  { label: 'DELETE_POST', value: 16 },
  { label: 'RESTORE_POST', value: 17 },
  { label: 'HARD_DELETE_POST', value: 18 },
  { label: 'DELETE_COMMENT', value: 20 },
  { label: 'RESTORE_COMMENT', value: 21 },
  { label: 'HARD_DELETE_COMMENT', value: 22 }
])

// 目标类型选项
const targetTypes = [
  { label: t('admin.activity.filterAllTargets'), value: '' },
  { label: 'POST', value: 3 },
  { label: 'COMMENT', value: 4 },
  { label: 'USER', value: 2 },
  { label: 'COMMUNITY', value: 1 }
]

// 目标类型映射
function getTargetTypeLabel(val) {
  const map = { 1: 'Community', 2: 'User', 3: 'Post', 4: 'Comment' }
  return map[val] || val
}

// 操作类型数字转英文名称映射
const actionTypeNames = {
  1: 'JOIN_COMMUNITY',
  2: 'LEAVE_COMMUNITY',
  3: 'BAN_USER',
  4: 'UNBAN_USER',
  5: 'TRANSFER_OWNERSHIP',
  6: 'PROMOTE_ADMIN',
  7: 'DEMOTE_ADMIN',
  10: 'LOCK_POST',
  11: 'UNLOCK_POST',
  12: 'HIGHLIGHT_POST',
  13: 'UNHIGHLIGHT_POST',
  14: 'PIN_POST',
  15: 'UNPIN_POST',
  16: 'DELETE_POST',
  17: 'RESTORE_POST',
  18: 'HARD_DELETE_POST',
  20: 'DELETE_COMMENT',
  21: 'RESTORE_COMMENT',
  22: 'HARD_DELETE_COMMENT',
  30: 'ADMIN_DELETE_POST',
  31: 'ADMIN_RESTORE_POST',
  32: 'ADMIN_HARD_DELETE_POST',
  33: 'ADMIN_DELETE_COMMENT',
  34: 'ADMIN_HARD_DELETE_COMMENT',
  35: 'ADMIN_RESTORE_COMMENT'
}

// 操作类型标签颜色
function getActionTypeTag(type) {
  const map = {
    1: 'success',   // JOIN_COMMUNITY
    2: '',          // LEAVE_COMMUNITY
    3: 'warning',   // BAN_USER
    4: 'success',   // UNBAN_USER
    5: '',          // TRANSFER_OWNERSHIP
    6: 'success',   // PROMOTE_ADMIN
    7: '',          // DEMOTE_ADMIN
    10: 'warning',  // LOCK_POST
    11: 'success',  // UNLOCK_POST
    12: 'warning',  // HIGHLIGHT_POST
    13: '',         // UNHIGHLIGHT_POST
    14: 'warning',  // PIN_POST
    15: '',         // UNPIN_POST
    16: 'danger',   // DELETE_POST
    17: 'success',  // RESTORE_POST
    18: 'danger',   // HARD_DELETE_POST
    20: 'danger',   // DELETE_COMMENT
    21: 'success',  // RESTORE_COMMENT
    22: 'danger',   // HARD_DELETE_COMMENT
    30: 'danger',   // ADMIN_DELETE_POST
    31: 'success',  // ADMIN_RESTORE_POST
    32: 'danger',   // ADMIN_HARD_DELETE_POST
    33: 'danger',   // ADMIN_DELETE_COMMENT
    34: 'danger',   // ADMIN_HARD_DELETE_COMMENT
    35: 'success'   // ADMIN_RESTORE_COMMENT
  }
  return map[type] || 'info'
}

// 获取操作类型的中文名称
function getActionTypeLabel(type) {
  return actionTypeNames[type] || `UNKNOWN_${type}`
}

async function fetchData() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (actionTypeFilter.value !== '') params.action_type = actionTypeFilter.value
    if (targetTypeFilter.value !== '') params.target_type = targetTypeFilter.value
    const res = await getAuditLogs(params)
    items.value = res.items || []
    total.value = res.total || 0
  } catch {
    items.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

function handlePageChange(newPage) {
  page.value = newPage
  fetchData()
}

watch([actionTypeFilter, targetTypeFilter], () => {
  page.value = 1
  fetchData()
})

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="admin-page">
    <div class="page-header">
      <div class="header-top">
        <div class="header-title">
          <h1>{{ t('admin.activity.title') }}</h1>
          <p>{{ t('admin.activity.description') }}</p>
        </div>
        <span class="header-count">{{ t('common.total', { count: total }) }}</span>
      </div>
    </div>

    <div class="toolbar">
      <el-select
        v-model="actionTypeFilter"
        :placeholder="t('admin.activity.filterAllTypes')"
        clearable
        style="width: 180px"
      >
        <el-option
          v-for="item in actionTypes"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-select
        v-model="targetTypeFilter"
        :placeholder="t('admin.activity.filterAllTargets')"
        clearable
        style="width: 160px"
      >
        <el-option
          v-for="item in targetTypes"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
    </div>

    <el-table
      v-loading="loading"
      :data="items"
      stripe
      style="width: 100%"
      :empty-text="t('admin.activity.noData')"
    >
      <el-table-column :label="t('admin.activity.columnActor')" width="140">
        <template #default="{ row }">
          {{ row.actor_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.activity.columnAction')" width="180" align="center">
        <template #default="{ row }">
          <el-tag :type="getActionTypeTag(row.action_type)" size="small">
            {{ getActionTypeLabel(row.action_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.activity.columnTargetType')" width="120" align="center">
        <template #default="{ row }">
          <el-tag type="info" size="small">
            {{ getTargetTypeLabel(row.target_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.activity.columnTargetId')" width="90" align="center">
        <template #default="{ row }">
          {{ row.target_id || '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.activity.columnReason')" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.reason || '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.activity.columnTimestamp')" width="170">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="handlePageChange"
        @size-change="(size) => { pageSize = size; page = 1; fetchData() }"
      />
    </div>
  </div>
</template>

<style scoped>
.admin-page {
  max-width: 1200px;
}

.page-header {
  margin-bottom: 20px;
}
.page-header h1 {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 6px;
}
.page-header p {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.header-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.header-title {
  flex: 1;
}

.header-count {
  font-size: 14px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 6px 12px;
  border-radius: 6px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
