<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getComments, deleteComment, restoreComment, hardDeleteComment } from '@/api/admin'
import { useFormatTime } from '@/composables/useFormatTime'

const router = useRouter()
const { t } = useI18n()
const { formatTime } = useFormatTime()

const searchText = ref('')
const includeDeleted = ref(false)

const loading = ref(false)
const items = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

async function fetchData() {
  loading.value = true
  try {
    const res = await getComments({
      page: page.value,
      page_size: pageSize.value,
      ...(searchText.value ? { search: searchText.value } : {}),
      ...(includeDeleted.value ? { include_deleted: true } : {})
    })
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

// 软删除
const handleSoftDelete = (row) => {
  ElMessageBox.confirm(
    t('admin.comments.confirmDelete'),
    t('common.confirm'),
    { confirmButtonText: t('admin.comments.deleteBtn'), cancelButtonText: t('common.cancel'), type: 'warning' }
  ).then(async () => {
    try {
      await deleteComment(row.id)
      ElMessage.success(t('admin.comments.deleteSuccess'))
      refresh()
    } catch {
      ElMessage.error(t('admin.comments.operationFailed'))
    }
  }).catch(() => {})
}

// 恢复
const handleRestore = (row) => {
  ElMessageBox.confirm(
    t('admin.comments.confirmRestore'),
    t('common.confirm'),
    { confirmButtonText: t('admin.comments.restoreBtn'), cancelButtonText: t('common.cancel'), type: 'info' }
  ).then(async () => {
    try {
      await restoreComment(row.id)
      ElMessage.success(t('admin.comments.restoreSuccess'))
      refresh()
    } catch {
      ElMessage.error(t('admin.comments.operationFailed'))
    }
  }).catch(() => {})
}

// 硬删除
const handleHardDelete = (row) => {
  ElMessageBox.confirm(
    t('admin.comments.confirmHardDelete'),
    t('common.confirm'),
    { confirmButtonText: t('admin.comments.hardDeleteBtn'), cancelButtonText: t('common.cancel'), type: 'error' }
  ).then(async () => {
    try {
      await hardDeleteComment(row.id)
      ElMessage.success(t('admin.comments.hardDeleteSuccess'))
      refresh()
    } catch {
      ElMessage.error(t('admin.comments.operationFailed'))
    }
  }).catch(() => {})
}

// 跳转帖子详情
const goToPost = (id) => {
  router.push(`/admin/post/${id}`)
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

watch(includeDeleted, () => {
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
      <h1>{{ t('admin.comments.title') }}</h1>
      <p>{{ t('admin.comments.description') }}</p>
    </div>

    <div class="toolbar">
      <el-input
        v-model="searchText"
        :placeholder="t('admin.comments.searchPlaceholder')"
        clearable
        style="width: 280px"
        :prefix-icon="Search"
      />
      <el-switch
        v-model="includeDeleted"
        :active-text="t('admin.comments.includeDeleted')"
      />
    </div>

    <el-table
      v-loading="loading"
      :data="items"
      stripe
      style="width: 100%"
      :empty-text="t('admin.comments.noData')"
    >
      <el-table-column :label="t('admin.comments.columnContent')" min-width="220" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.content || '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.comments.columnAuthor')" width="140">
        <template #default="{ row }">
          {{ row.author?.username || '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.comments.columnPost')" width="100">
        <template #default="{ row }">
          <a v-if="row.post_id" class="link-post" @click="goToPost(row.post_id)">#{{ row.post_id }}</a>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.comments.columnStatus')" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_deleted ? 'danger' : 'success'" size="small">
            {{ row.is_deleted ? t('admin.comments.statusDeleted') : t('admin.comments.statusNormal') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.comments.columnCreatedAt')" width="170">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.comments.columnActions')" width="240" fixed="right">
        <template #default="{ row }">
          <div class="action-btns">
            <el-button
              v-if="!row.is_deleted"
              size="small"
              type="warning"
              @click="handleSoftDelete(row)"
            >{{ t('admin.comments.deleteBtn') }}</el-button>
            <el-button
              v-if="row.is_deleted"
              size="small"
              type="success"
              @click="handleRestore(row)"
            >{{ t('admin.comments.restoreBtn') }}</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleHardDelete(row)"
            >{{ t('admin.comments.hardDeleteBtn') }}</el-button>
          </div>
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
  gap: 16px;
  margin-bottom: 16px;
}

.link-post {
  color: var(--color-primary);
  cursor: pointer;
  text-decoration: none;
}
.link-post:hover {
  text-decoration: underline;
}

.action-btns {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
