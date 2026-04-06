<script setup>
import { ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getUsers, banUser, unbanUser } from '@/api/admin'
import { useFormatTime } from '@/composables/useFormatTime'

const { t } = useI18n()
const { formatTime } = useFormatTime()

const searchText = ref('')
const statusFilter = ref('')
const roleFilter = ref('')

const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

async function fetchData() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    if (searchText.value) params.search = searchText.value
    if (statusFilter.value !== '') params.is_active = statusFilter.value === 'active'
    if (roleFilter.value !== '') params.is_superuser = roleFilter.value === 'superuser'
    const res = await getUsers(params)
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

function refresh() {
  fetchData()
}

// 封禁
const handleBan = (row) => {
  ElMessageBox.confirm(
    t('admin.users.confirmBan'),
    t('common.confirm'),
    { confirmButtonText: t('admin.users.banBtn'), cancelButtonText: t('common.cancel'), type: 'warning' }
  ).then(async () => {
    try {
      await banUser(row.id)
      ElMessage.success(t('admin.users.banSuccess'))
      refresh()
    } catch {
      ElMessage.error(t('admin.users.operationFailed'))
    }
  }).catch(() => {})
}

// 解封
const handleUnban = (row) => {
  ElMessageBox.confirm(
    t('admin.users.confirmUnban'),
    t('common.confirm'),
    { confirmButtonText: t('admin.users.unbanBtn'), cancelButtonText: t('common.cancel'), type: 'info' }
  ).then(async () => {
    try {
      await unbanUser(row.id)
      ElMessage.success(t('admin.users.unbanSuccess'))
      refresh()
    } catch {
      ElMessage.error(t('admin.users.operationFailed'))
    }
  }).catch(() => {})
}

// 搜索防抖
let searchTimer = null
watch(searchText, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchData()
  }, 300)
})

watch([statusFilter, roleFilter], () => {
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
      <h1>{{ t('admin.users.title') }}</h1>
      <p>{{ t('admin.users.description') }}</p>
    </div>

    <div class="toolbar">
      <el-input
        v-model="searchText"
        :placeholder="t('admin.users.searchPlaceholder')"
        clearable
        style="width: 280px"
        :prefix-icon="Search"
      />
      <el-select
        v-model="statusFilter"
        :placeholder="t('admin.users.filterAll')"
        clearable
        style="width: 140px"
      >
        <el-option :label="t('admin.users.filterAll')" value="" />
        <el-option :label="t('admin.users.filterActive')" value="active" />
        <el-option :label="t('admin.users.filterInactive')" value="inactive" />
      </el-select>
      <el-select
        v-model="roleFilter"
        :placeholder="t('admin.users.filterAll')"
        clearable
        style="width: 140px"
      >
        <el-option :label="t('admin.users.filterAll')" value="" />
        <el-option :label="t('admin.users.filterSuperuser')" value="superuser" />
        <el-option :label="t('admin.users.filterRegular')" value="regular" />
      </el-select>
    </div>

    <el-table
      v-loading="loading"
      :data="items"
      stripe
      style="width: 100%"
      :empty-text="t('admin.users.noData')"
    >
      <el-table-column :label="t('admin.users.columnUsername')" width="160">
        <template #default="{ row }">
          {{ row.username }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.users.columnEmail')" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.email || '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.users.columnStatus')" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? t('admin.users.statusActive') : t('admin.users.statusInactive') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.users.columnRole')" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_superuser ? 'warning' : 'info'" size="small">
            {{ row.is_superuser ? t('admin.users.roleSuperuser') : t('admin.users.roleUser') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.users.columnCreatedAt')" width="170">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.users.columnActions')" width="120" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.is_active"
            size="small"
            type="danger"
            @click="handleBan(row)"
          >{{ t('admin.users.banBtn') }}</el-button>
          <el-button
            v-else
            size="small"
            type="success"
            @click="handleUnban(row)"
          >{{ t('admin.users.unbanBtn') }}</el-button>
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
