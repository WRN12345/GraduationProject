<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'
import {
  Clock,
  ChevronDown,
  Search,
  LogOut,
  ArrowLeft
} from 'lucide-vue-next'
import { useAdminTimeFilter } from '@/composables/useAdminTimeFilter'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const userStore = useUserStore()

const {
  selectedRange,
  setRange,
  setCustomRange
} = useAdminTimeFilter()

// ---- Breadcrumb ----
const ROUTE_CRUMBS = {
  '/admin':           { key: 'admin.sidebar.dashboard', path: '/admin' },
  '/admin/posts':     { key: 'admin.sidebar.posts',     path: '/admin/posts' },
  '/admin/comments':  { key: 'admin.sidebar.comments',  path: '/admin/comments' },
  '/admin/users':     { key: 'admin.sidebar.users',     path: '/admin/users' },
  '/admin/activity':  { key: 'admin.sidebar.activity',   path: '/admin/activity' }
}

const breadcrumbs = computed(() => {
  const crumbs = [{ label: t(ROUTE_CRUMBS['/admin'].key), path: '/admin' }]
  const path = route.path

  if (ROUTE_CRUMBS[path] && path !== '/admin') {
    crumbs.push({ label: t(ROUTE_CRUMBS[path].key), path: ROUTE_CRUMBS[path].path })
  } else if (path.startsWith('/admin/post/')) {
    crumbs.push({ label: t('admin.sidebar.posts'), path: '/admin/posts' })
    crumbs.push({ label: t('breadcrumb.postDetail'), path: null })
  }

  return crumbs
})

// ---- Time Filter ----
const showCustomDatePicker = ref(false)

const currentFilterLabel = computed(() => {
  const labels = {
    '24h':   t('admin.header.last24h'),
    '7d':    t('admin.header.last7d'),
    '30d':   t('admin.header.last30d'),
    'custom': t('admin.header.customRange')
  }
  return labels[selectedRange.value] || t('admin.header.last7d')
})

function handleTimeFilterChange(command) {
  if (command === 'custom') {
    showCustomDatePicker.value = true
  } else {
    showCustomDatePicker.value = false
    setRange(command)
  }
}

const customDateRange = ref(null)

function handleCustomDateChange(val) {
  if (val && val.length === 2) {
    setCustomRange(val[0], val[1])
  }
}

// ---- Search ----
const searchQuery = ref('')

function handleSearch() {
  const q = searchQuery.value.trim()
  if (!q) return
  router.push({ path: '/admin/posts', query: { q } })
}

// ---- Avatar / Dropdown ----
const userInfo = computed(() => userStore.userInfo)

const avatarInitial = computed(() => {
  const name = userInfo.value?.username || userInfo.value?.nickname || ''
  return name.charAt(0).toUpperCase() || 'A'
})

function handleAvatarCommand(command) {
  switch (command) {
    case 'logout':
      userStore.logout().then(() => router.push('/login'))
      break
    case 'backToSite':
      router.push('/')
      break
  }
}
</script>

<template>
  <header class="admin-header">
    <!-- Left: Breadcrumb -->
    <div class="admin-header__left">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item
          v-for="(crumb, idx) in breadcrumbs"
          :key="idx"
          :to="crumb.path ? { path: crumb.path } : undefined"
        >
          {{ crumb.label }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- Right: Actions -->
    <div class="admin-header__right">
      <!-- Time filter -->
      <el-dropdown trigger="click" @command="handleTimeFilterChange">
        <span class="filter-trigger">
          <Clock :size="14" />
          <span class="filter-label">{{ currentFilterLabel }}</span>
          <ChevronDown :size="12" />
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="24h">{{ t('admin.header.last24h') }}</el-dropdown-item>
            <el-dropdown-item command="7d">{{ t('admin.header.last7d') }}</el-dropdown-item>
            <el-dropdown-item command="30d">{{ t('admin.header.last30d') }}</el-dropdown-item>
            <el-dropdown-item command="custom" divided>{{ t('admin.header.customRange') }}</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <!-- Custom date range picker -->
      <el-date-picker
        v-if="showCustomDatePicker"
        v-model="customDateRange"
        type="daterange"
        :start-placeholder="t('admin.header.customRange')"
        :end-placeholder="t('admin.header.customRange')"
        size="small"
        value-format="YYYY-MM-DD"
        style="width: 240px"
        @change="handleCustomDateChange"
      />

      <!-- Quick search -->
      <div class="admin-search">
        <el-input
          v-model="searchQuery"
          :placeholder="t('admin.header.searchPlaceholder')"
          clearable
          :prefix-icon="Search"
          size="default"
          style="width: 220px"
          @keyup.enter="handleSearch"
        />
      </div>

      <!-- Avatar dropdown -->
      <el-dropdown trigger="click" @command="handleAvatarCommand">
        <div class="avatar-trigger">
          <img v-if="userInfo?.avatar" :src="userInfo.avatar" alt="avatar" />
          <div v-else class="avatar-fallback">{{ avatarInitial }}</div>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="backToSite">
              <ArrowLeft :size="14" style="margin-right: 6px" />
              {{ t('admin.header.backToSite') }}
            </el-dropdown-item>
            <el-dropdown-item command="logout" divided>
              <LogOut :size="14" style="margin-right: 6px" />
              {{ t('admin.header.logout') }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<style scoped>
.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  padding: 0 4px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color-light, var(--border-light));
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.admin-header__left {
  flex-shrink: 0;
  min-width: 0;
}

.admin-header__right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

/* Time filter trigger */
.filter-trigger {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  white-space: nowrap;
  user-select: none;
}

.filter-trigger:hover {
  color: var(--color-primary);
  background: var(--bg-secondary);
}

.filter-label {
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Search */
.admin-search {
  display: flex;
  align-items: center;
}

/* Avatar */
.avatar-trigger {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 1.5px solid var(--border-color-light, var(--border-light));
  transition: border-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar-trigger:hover {
  border-color: var(--color-primary);
}

.avatar-trigger img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-fallback {
  width: 100%;
  height: 100%;
  background: var(--color-primary);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Responsive */
@media (max-width: 767px) {
  .filter-label {
    display: none;
  }

  .admin-search :deep(.el-input) {
    width: 160px !important;
  }

  .admin-header {
    padding: 0 8px;
  }
}
</style>
