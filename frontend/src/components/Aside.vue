<script setup>
import { useRouter } from 'vue-router'
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
  X,
  Building2
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
      <div class="nav-item active" @click="navigateTo('/')">
        <Home :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">主页</span>
      </div>
      <div class="nav-item">
        <TrendingUp :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">受欢迎</span>
      </div>
      <div class="nav-item">
        <Compass :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">浏览</span>
      </div>
      <div class="nav-item">
        <Globe :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">全部</span>
      </div>
      <div class="nav-item">
        <PlusCircle :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">加入社区</span>
      </div>
    </nav>

    <div class="divider" v-if="!isCollapsed"></div>

    <div class="section-title" v-if="!isCollapsed">社区</div>
    <nav class="nav-group">
      <div class="nav-item" @click="navigateTo('/communities')">
        <Building2 :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">创建社区</span>
      </div>
      <div class="nav-item" @click="navigateTo('/my-communities')">
        <Users :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">我的社区</span>
      </div>
      <div class="nav-item">
        <Settings :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">设置</span>
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
      <div class="nav-item">
        <Bookmark :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">收藏夹</span>
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
  color: #1c1c1c;
  font-size: 14px;
  transition: all 0.2s ease;
  width: 100%;
}

.nav-item:hover {
  background-color: #f6f7f8;
}

.nav-item.active {
  background-color: #f6f7f8;
  font-weight: 600;
}

.icon {
  min-width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1c1c1c;
  flex-shrink: 0;
}

.text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.divider {
  height: 1px;
  background-color: #edeff1;
  margin: 15px 0;
}

.section-title {
  font-size: 12px;
  color: #878a8c;
  text-transform: uppercase;
  font-weight: 700;
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