<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getPosts, deletePost, restorePost, hardDeletePost } from '@/api/admin'
import { useAdminTable } from '@/composables/useAdminTable'
import { useFormatTime } from '@/composables/useFormatTime'

const router = useRouter()
const { t } = useI18n()
const { formatTime } = useFormatTime()

const searchText = ref('')
const includeDeleted = ref(false)

const {
  loading,
  items,
  total,
  page,
  pageSize,
  fetchData,
  handlePageChange,
  refresh
} = useAdminTable(getPosts)

// 软删除
const handleSoftDelete = (row) => {
  ElMessageBox.confirm(
    t('admin.posts.confirmDelete'),
    t('common.confirm'),
    { confirmButtonText: t('admin.posts.deleteBtn'), cancelButtonText: t('common.cancel'), type: 'warning' }
  ).then(async () => {
    try {
      await deletePost(row.id)
      ElMessage.success(t('admin.posts.deleteSuccess'))
      refresh()
    } catch {
      ElMessage.error(t('admin.posts.operationFailed'))
    }
  }).catch(() => {})
}

// 恢复
const handleRestore = (row) => {
  ElMessageBox.confirm(
    t('admin.posts.confirmRestore'),
    t('common.confirm'),
    { confirmButtonText: t('admin.posts.restoreBtn'), cancelButtonText: t('common.cancel'), type: 'info' }
  ).then(async () => {
    try {
      await restorePost(row.id)
      ElMessage.success(t('admin.posts.restoreSuccess'))
      refresh()
    } catch {
      ElMessage.error(t('admin.posts.operationFailed'))
    }
  }).catch(() => {})
}

// 硬删除
const handleHardDelete = (row) => {
  ElMessageBox.confirm(
    t('admin.posts.confirmHardDelete'),
    t('common.confirm'),
    { confirmButtonText: t('admin.posts.hardDeleteBtn'), cancelButtonText: t('common.cancel'), type: 'error' }
  ).then(async () => {
    try {
      await hardDeletePost(row.id)
      ElMessage.success(t('admin.posts.hardDeleteSuccess'))
      refresh()
    } catch {
      ElMessage.error(t('admin.posts.operationFailed'))
    }
  }).catch(() => {})
}

// 跳转帖子详情
const goToPost = (id) => {
  router.push(`/admin/post/${id}`)
}

// 搜索防抖
let searchTimer = null
watch(searchText, (val) => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    items.value = []
    total.value = 0
    getPosts({
      page: 1,
      page_size: pageSize.value,
      ...(val ? { search: val } : {}),
      ...(includeDeleted.value ? { include_deleted: true } : {})
    }).then((res) => {
      items.value = res.items || []
      total.value = res.total || 0
    }).catch(() => {})
  }, 300)
})

// 切换包含已删除
watch(includeDeleted, () => {
  getPosts({
    page: 1,
    page_size: pageSize.value,
    ...(searchText.value ? { search: searchText.value } : {}),
    ...(includeDeleted.value ? { include_deleted: true } : {})
  }).then((res) => {
    items.value = res.items || []
    total.value = res.total || 0
    page.value = 1
  }).catch(() => {})
})

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="admin-page">
    <div class="page-header">
      <h1>{{ t('admin.posts.title') }}</h1>
      <p>{{ t('admin.posts.description') }}</p>
    </div>

    <div class="toolbar">
      <el-input
        v-model="searchText"
        :placeholder="t('admin.posts.searchPlaceholder')"
        clearable
        style="width: 280px"
        :prefix-icon="Search"
      />
      <el-switch
        v-model="includeDeleted"
        :active-text="t('admin.posts.includeDeleted')"
      />
    </div>

    <el-table
      v-loading="loading"
      :data="items"
      stripe
      style="width: 100%"
      :empty-text="t('admin.posts.noData')"
    >
      <el-table-column :label="t('admin.posts.columnTitle')" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <a class="link-title" @click="goToPost(row.id)">{{ row.title }}</a>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.posts.columnAuthor')" width="140">
        <template #default="{ row }">
          {{ row.author?.username || '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.posts.columnCommunity')" width="150">
        <template #default="{ row }">
          {{ row.community?.name || '-' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.posts.columnStatus')" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_deleted ? 'danger' : 'success'" size="small">
            {{ row.is_deleted ? t('admin.posts.statusDeleted') : t('admin.posts.statusNormal') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.posts.columnCreatedAt')" width="170">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column :label="t('admin.posts.columnActions')" width="240" fixed="right">
        <template #default="{ row }">
          <div class="action-btns">
            <el-button
              v-if="!row.is_deleted"
              size="small"
              type="warning"
              @click="handleSoftDelete(row)"
            >{{ t('admin.posts.deleteBtn') }}</el-button>
            <el-button
              v-if="row.is_deleted"
              size="small"
              type="success"
              @click="handleRestore(row)"
            >{{ t('admin.posts.restoreBtn') }}</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleHardDelete(row)"
            >{{ t('admin.posts.hardDeleteBtn') }}</el-button>
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

.link-title {
  color: var(--color-primary);
  cursor: pointer;
  text-decoration: none;
}
.link-title:hover {
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
