<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
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
  Clipboard,
  Sun,
  Moon,
  ChevronDown,
  ChevronRight,
  Languages
} from 'lucide-vue-next'
import { useThemeStore } from '@/stores/theme'

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
const { t, locale } = useI18n()
const themeStore = useThemeStore()

const isSettingsExpanded = ref(false)

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

const toggleSettings = () => {
  isSettingsExpanded.value = !isSettingsExpanded.value
}

const switchLanguage = (lang) => {
  locale.value = lang
  localStorage.setItem('locale', lang)
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
        <span v-if="!isCollapsed" class="text">{{ t('aside.home') }}</span>
      </div>
      <div class="nav-item" :class="{ active: isActive('/trending') }" @click="navigateTo('/trending')">
        <TrendingUp :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">{{ t('aside.trending') }}</span>
      </div>
      <div class="nav-item" :class="{ active: isActive('/bookmarks') }" @click="navigateTo('/bookmarks')">
        <Bookmark :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">{{ t('aside.bookmarks') }}</span>
      </div>
      <div class="nav-item" :class="{ active: isActive('/my-posts') }" @click="navigateTo('/my-posts')">
        <FileText :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">{{ t('aside.myPosts') }}</span>
      </div>
      <div class="nav-item" :class="{ active: isActive('/drafts') }" @click="navigateTo('/drafts')">
        <Clipboard :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">{{ t('aside.drafts') }}</span>
      </div>
    </nav>

    <div class="divider" v-if="!isCollapsed"></div>

    <div class="section-title" v-if="!isCollapsed">{{ t('aside.community') }}</div>
    <nav class="nav-group">
      <div class="nav-item" :class="{ active: isActive('/my-communities') }" @click="navigateTo('/my-communities')">
        <Users :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">{{ t('aside.myCommunities') }}</span>
      </div>
      <div class="nav-item" :class="{ active: isActive('/all-communities') }" @click="navigateTo('/all-communities')">
        <Compass :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">{{ t('aside.allCommunities') }}</span>
      </div>
    </nav>

    <div class="divider" v-if="!isCollapsed"></div>

    <div class="section-title" v-if="!isCollapsed">{{ t('aside.settings') }}</div>
    <nav class="nav-group">
      <!-- 系统设置 - 可展开 -->
      <div class="nav-item settings-toggle" @click="toggleSettings">
        <Settings :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">{{ t('aside.systemSettings') }}</span>
        <ChevronDown
          v-if="!isCollapsed"
          :size="16"
          class="expand-icon"
          :class="{ rotated: isSettingsExpanded }"
        />
      </div>

      <!-- 设置子菜单 -->
      <transition name="slide">
        <div v-if="isSettingsExpanded && !isCollapsed" class="settings-submenu">
          <!-- 主题切换 -->
          <div class="setting-item">
            <div class="setting-label">
              <Sun v-if="!themeStore.isDark" :size="16" class="setting-icon" />
              <Moon v-else :size="16" class="setting-icon" />
              <span>{{ t('aside.theme') }}</span>
            </div>
            <div class="theme-switch" @click="themeStore.toggleTheme()">
              <div class="theme-switch-track" :class="{ dark: themeStore.isDark }">
                <div class="theme-switch-thumb">
                  <Sun v-if="!themeStore.isDark" :size="12" />
                  <Moon v-else :size="12" />
                </div>
              </div>
            </div>
          </div>

          <!-- 语言设置 -->
          <div class="setting-item">
            <div class="setting-label">
              <Languages :size="16" class="setting-icon" />
              <span>{{ t('aside.language') }}</span>
            </div>
            <div class="lang-switch">
              <button
                class="lang-btn"
                :class="{ active: locale === 'zh-CN' }"
                @click="switchLanguage('zh-CN')"
              >
                中
              </button>
              <button
                class="lang-btn"
                :class="{ active: locale === 'en' }"
                @click="switchLanguage('en')"
              >
                EN
              </button>
            </div>
          </div>
        </div>
      </transition>
    </nav>

    <div class="divider" v-if="!isCollapsed"></div>

    <div class="section-title" v-if="!isCollapsed">{{ t('aside.privacy') }}</div>
    <nav class="nav-group">
      <div class="nav-item">
        <Lock :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">{{ t('aside.privacySettings') }}</span>
      </div>
      <div class="nav-item">
        <Shield :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">{{ t('aside.securityCenter') }}</span>
      </div>
      <div class="nav-item">
        <Eye :size="20" class="icon" />
        <span v-if="!isCollapsed" class="text">{{ t('aside.history') }}</span>
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
  background: var(--bg-secondary);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  padding: 8px;
  color: var(--text-primary);
  transition: background 0.2s;
  z-index: 10;
}

.mobile-close-btn:hover {
  background: var(--bg-hover);
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
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 400;
  transition: all 0.2s ease;
  width: 100%;
  position: relative;
  margin: 2px 0;
}

.nav-item:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background-color: var(--bg-active);
  color: var(--color-primary);
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
  background: linear-gradient(180deg, var(--color-primary), var(--color-primary-light));
  border-radius: 0 3px 3px 0;
}

.icon {
  min-width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
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
  flex: 1;
}

.divider {
  height: 1px;
  background-color: var(--border-color);
  margin: 12px 0;
}

.section-title {
  font-size: 11px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
  padding-left: 12px;
}

/* === 设置展开按钮 === */
.settings-toggle {
  position: relative;
}

.expand-icon {
  margin-left: auto;
  transition: transform 0.3s ease;
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

/* === 设置子菜单 === */
.settings-submenu {
  padding: 4px 0 4px 12px;
  overflow: hidden;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 8px;
  margin: 2px 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.setting-item:hover {
  background-color: var(--bg-hover);
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-icon {
  color: var(--text-tertiary);
}

/* === 主题切换开关 === */
.theme-switch {
  cursor: pointer;
  flex-shrink: 0;
}

.theme-switch-track {
  width: 48px;
  height: 26px;
  border-radius: 13px;
  background: linear-gradient(135deg, #f0c27f, #4b1248);
  position: relative;
  transition: background 0.3s ease;
  display: flex;
  align-items: center;
  padding: 2px;
}

.theme-switch-track.dark {
  background: linear-gradient(135deg, #0f2027, #203a43);
}

.theme-switch-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  color: #f59e0b;
}

.theme-switch-track.dark .theme-switch-thumb {
  transform: translateX(22px);
  color: #6366f1;
}

/* === 语言切换按钮 === */
.lang-switch {
  display: flex;
  gap: 2px;
  background: var(--bg-secondary);
  border-radius: 6px;
  padding: 2px;
  flex-shrink: 0;
}

.lang-btn {
  padding: 3px 10px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.lang-btn.active {
  background: var(--color-primary);
  color: var(--text-inverse);
}

.lang-btn:hover:not(.active) {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* === 展开/收起动画 === */
.slide-enter-active {
  transition: all 0.3s ease;
}

.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
}

.slide-enter-to {
  max-height: 200px;
  opacity: 1;
}

.slide-leave-from {
  max-height: 200px;
  opacity: 1;
}

.slide-leave-to {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
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
