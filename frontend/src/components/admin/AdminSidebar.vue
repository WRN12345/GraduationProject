<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  LayoutDashboard,
  FileText,
  MessageSquare,
  History,
  Users,
  ArrowLeft,
  ShieldCheck
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const menuItems = computed(() => [
  {
    icon: LayoutDashboard,
    label: t('admin.sidebar.dashboard'),
    path: '/admin',
    active: route.path === '/admin'
  },
  {
    icon: FileText,
    label: t('admin.sidebar.posts'),
    path: '/admin/posts',
    active: route.path === '/admin/posts'
  },
  {
    icon: MessageSquare,
    label: t('admin.sidebar.comments'),
    path: '/admin/comments',
    active: route.path === '/admin/comments'
  },
  {
    icon: Users,
    label: t('admin.sidebar.users'),
    path: '/admin/users',
    active: route.path === '/admin/users'
  },
  {
    icon: History,
    label: t('admin.sidebar.activity'),
    path: '/admin/activity',
    active: route.path === '/admin/activity'
  }
])

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <aside class="admin-sidebar">
    <div class="sidebar-header">
      <div class="sidebar-title">
        <ShieldCheck :size="20" class="title-icon" />
        <span>{{ t('admin.sidebar.title') }}</span>
      </div>
      <button class="back-btn" @click="goBack" :title="t('admin.sidebar.backToSite')">
        <ArrowLeft :size="16" />
      </button>
    </div>

    <nav class="sidebar-nav">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: item.active }"
      >
        <component :is="item.icon" :size="18" class="nav-icon" />
        <span class="nav-label">{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<style scoped>
.admin-sidebar {
  width: 220px;
  min-width: 220px;
  height: calc(100vh - 48px);
  position: sticky;
  top: 48px;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-color-light);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color-light);
}

.sidebar-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.title-icon {
  color: #ff4500;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.15s;
}

.back-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.sidebar-nav {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  transition: all 0.15s;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background: #fff3e6;
  color: #ff4500;
}

:root.dark .nav-item.active {
  background: rgba(255, 69, 0, 0.15);
}

.nav-icon {
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
