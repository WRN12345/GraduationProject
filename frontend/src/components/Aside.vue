<script setup>
import { useRouter, useRoute } from 'vue-router'
import {
  Home,
  TrendingUp,
  Compass,
  Globe,
  PlusCircle,
  Users,
  Settings,
  Lock,
  Shield,
  Eye,
  Bookmark,
  FileText,
  X,
  Clipboard
} from 'lucide-vue-next'

defineProps({
  isCollapsed: {
    type: Boolean,
    default: false
  },
  isMobileOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close-mobile'])

const router = useRouter()
const route = useRoute()

// 判断当前路由是否匹配指定路径
const isActive = (path) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

const closeMobileSidebar = () => {
  emit('close-mobile')
}

const navigateTo = (path) => {
  router.push(path)
  closeMobileSidebar()
}
</script>

<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed, 'mobile-open': isMobileOpen }">
    <!-- 移动端关闭按钮 -->
    <button class="mobile-close-btn" @click="closeMobileSidebar" v-if="isMobileOpen">
      <X :size="20" />
    </button>

    <nav class="nav-group">
      <div class="nav-item" :class="{ active: isActive('/') }" @click="navigateTo('/')">
        <Home :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">主页</span>
      </div>
      <div class="nav-item" :class="{ active: isActive('/trending') }" @click="navigateTo('/trending')">
        <TrendingUp :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">受欢迎</span>
      </div>
      <div class="nav-item" :class="{ active: isActive('/bookmarks') }" @click="navigateTo('/bookmarks')">
        <Bookmark :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">收藏夹</span>
      </div>
      <div class="nav-item" :class="{ active: isActive('/my-posts') }" @click="navigateTo('/my-posts')">
        <FileText :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">我的帖子</span>
      </div>
      <div class="nav-item" :class="{ active: isActive('/drafts') }" @click="navigateTo('/drafts')">
        <Clipboard :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">草稿箱</span>
      </div>
    </nav>

    <div class="divider" v-if="!isCollapsed"></div>

    <div class="section-title" v-if="!isCollapsed">社区</div>
    <nav class="nav-group">
      <div class="nav-item" :class="{ active: isActive('/my-communities') }" @click="navigateTo('/my-communities')">
        <Users :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">我的社区</span>
      </div>
      <div class="nav-item" :class="{ active: isActive('/all-communities') }" @click="navigateTo('/all-communities')">
        <Compass :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">全部社区</span>
      </div>
    </nav>

    <div class="divider" v-if="!isCollapsed"></div>

    <div class="section-title" v-if="!isCollapsed">设置</div>
    <nav class="nav-group">
      <div class="nav-item">
        <Settings :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">系统设置</span>
      </div>
    </nav>

    <div class="divider" v-if="!isCollapsed"></div>

    <div class="section-title" v-if="!isCollapsed">隐私</div>
    <nav class="nav-group">
      <div class="nav-item">
        <Lock :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">隐私设置</span>
      </div>
      <div class="nav-item">
        <Shield :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">安全中心</span>
      </div>
      <div class="nav-item">
        <Eye :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">历史记录</span>
      </div>
    </nav>
    <div class="divider" v-if="!isCollapsed"></div>
  </aside>
</template>

<style scoped>
.sidebar {
  padding-bottom: 20px;
  transition: all 0.3s ease;
}

/* 移动端关闭按钮 */
.mobile-close-btn {
  display: none;
  position: absolute;
  top: 12px;
  right: 12px;
  background: #f6f7f8;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  padding: 8px;
  color: #1c1c1c;
  transition: background 0.2s;
  z-index: 10;
}

.mobile-close-btn:hover {
  background: #edeff1;
}

.sidebar.collapsed {
  padding: 0;
}

.sidebar.collapsed .nav-item {
  justify-content: flex-start;
  padding: 10px 0 10px 12px;
  width: 100%;
}

.nav-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #666;
  font-size: 13px;
  font-weight: 400;
  transition: all 0.2s ease;
  width: 100%;
  position: relative;
  margin: 2px 0;
}

.nav-item:hover {
  background-color: #f5f5f5;
  color: #333;
}

.nav-item.active {
  background-color: #f0f7ff;
  color: #0079d3;
  font-weight: 500;
}

/* 选中状态指示线 */
.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: linear-gradient(180deg, #0079d3, #00a0ff);
  border-radius: 0 3px 3px 0;
}

.icon {
  min-width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #777;
  flex-shrink: 0;
  transition: color 0.2s ease;
}

.nav-item:hover .icon,
.nav-item.active .icon {
  color: inherit;
}

.text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.divider {
  height: 1px;
  background-color: #e8e8e8;
  margin: 12px 0;
}

.section-title {
  font-size: 11px;
  color: #999;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
  padding-left: 12px;
}

/* === 响应式断点 === */

/* 小窗口 (< 640px) */
@media (max-width: 639px) {
  .mobile-close-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sidebar {
    padding-top: 50px;
  }
}

/* 中小窗口 (640px - 767px) */
@media (min-width: 640px) and (max-width: 767px) {
  .mobile-close-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sidebar {
    padding-top: 50px;
  }
}

/* 中等窗口 (768px - 959px) */
@media (min-width: 768px) and (max-width: 959px) {
  .mobile-close-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sidebar {
    padding-top: 50px;
  }
}
</style>