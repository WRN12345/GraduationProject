<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search,
  MessageCircle,
  Plus,
  Bell,
  X,
  TrendingUp,
  Shirt,
  FileText,
  Trophy,
  DollarSign,
  Shield,
  Star,
  Moon,
  LogOut,
  Megaphone,
  Clock,
  Settings,
  ChevronDown,
  Menu
} from 'lucide-vue-next'
import { useUserStore } from '@/stores/user'

// 定义 emit
const emit = defineEmits(['open-mobile-sidebar'])

// 路由
const router = useRouter()

// --- 搜索相关逻辑 (保留之前的) ---
const searchText = ref('')
const isSearchFocused = ref(false)
const trendingList = ref([
  { id: 1, title: 'TGA 2025 Winners', desc: '年度游戏大奖公布', icon: 'Trophy' },
  { id: 2, title: 'Vue.js 3.5 Release', desc: '前端框架新版本', icon: 'TrendingUp' },
  { id: 3, title: 'GTA VI Leak', desc: '侠盗猎车手6最新泄露', icon: 'Gamepad2' },
])

const handleSearchBlur = () => {
  setTimeout(() => { isSearchFocused.value = false }, 200)
}
const handleSearchResultSelect = (item) => {
  searchText.value = item.title
  isSearchFocused.value = false
}

// --- 个人菜单相关逻辑  ---
const isProfileOpen = ref(false)
const isDarkMode = ref(false) // 模拟暗黑模式状态

const toggleProfile = () => {
  isProfileOpen.value = !isProfileOpen.value
  // 如果打开了个人菜单，关闭搜索下拉
  if (isProfileOpen.value) isSearchFocused.value = false
}

// 用户认证相关
const userStore = useUserStore()

const handleLogout = async () => {
  // 关闭个人菜单
  isProfileOpen.value = false

  // 调用登出方法
  await userStore.logout()

  // 登出成功后会自动跳转到登录页（通过路由守卫）
}

// 创建帖子
const goToCreatePost = () => {
  router.push('/create-post')
}

// 返回主页
const goToHome = () => {
  router.push('/')
}

// 获取图标组件
const getIcon = (iconName) => {
  const icons = {
    Trophy,
    TrendingUp,
    Gamepad2: Trophy, // Fallback to Trophy
  }
  return icons[iconName] || Trophy
}
</script>

<template>
  <header class="header-container">
    <!-- 汉堡菜单按钮（移动端） -->
    <button class="mobile-menu-btn" @click="emit('open-mobile-sidebar')" title="打开菜单">
      <Menu :size="24" />
    </button>

    <!-- 1. Logo 区域 -->
    <div class="logo-section" @click="goToHome" title="返回主页">
      <img src="@/assets/image/wrn.png" alt="Logo" class="logo-img" />
      <span class="logo-text">Super Dev</span>
    </div>

    <!-- 2. 搜索框区域 -->
    <div class="search-section">
      <div class="search-wrapper" :class="{ 'is-active': isSearchFocused }">
        <div class="search-bar">
          <Search :size="18" class="search-icon" />
          <input
            type="text"
            placeholder="查找所需一切信息"
            v-model="searchText"
            @focus="isSearchFocused = true"
            @blur="handleSearchBlur"
          />
          <X v-if="searchText" :size="16" class="clear-icon" @click="searchText = ''" />
        </div>
        <!-- 搜索下拉 (保留之前的代码) -->
        <div class="search-dropdown" v-if="isSearchFocused">
          <div class="dropdown-header">
            <TrendingUp :size="14" />
            <span>热门趋势</span>
          </div>
          <ul class="trending-list">
            <li v-for="item in trendingList" :key="item.id" class="trending-item" @click="handleSearchResultSelect(item)">
              <component :is="getIcon(item.icon)" :size="20" class="trend-icon" />
              <div class="trend-info">
                <div class="trend-title">{{ item.title }}</div>
                <div class="trend-desc">{{ item.desc }}</div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 3. 右侧功能区 -->
    <div class="actions-section">
      <button class="btn-icon" title="消息"><MessageCircle :size="20" /></button>
      <button class="btn-icon" title="创建" @click="goToCreatePost"><Plus :size="20" /><span>创建</span></button>
      <button class="btn-icon" title="通知"><Bell :size="20" /></button>

      <!-- 个人头像容器 (Dropdown Trigger) -->
      <div class="user-menu-container">
        <div class="avatar-trigger" @click="toggleProfile">
          <div class="avatar-box">
             <!-- 这里的图片可以换成你自己的 -->
             <div class="avatar-img-wrapper">
               <img src="@/assets/image/wrn.png" class="user-avatar-img" />
               <div class="status-dot"></div>
             </div>
          </div>
          <ChevronDown :size="12" class="dropdown-arrow" />
        </div>

        <!-- 个人下拉菜单 (核心新增部分) -->
        <div class="profile-dropdown" v-if="isProfileOpen">

          <!-- 第一部分：用户信息 -->
          <div class="menu-section user-info-section">
            <div class="menu-item-user">
              <div class="user-avatar-large">
                <img src="@/assets/image/wrn.png" />
                <div class="status-dot large"></div>
              </div>
              <div class="user-text-info">
                <div class="user-display-name">查看个人资料</div>
                <div class="user-handle">u/CapitalGreedy2260</div>
              </div>
            </div>
          </div>

          <!-- 第二部分：通用操作 -->
          <div class="menu-section">
            <div class="menu-item">
              <Shirt :size="20" class="menu-icon" />
              <span class="menu-text">编辑头像</span>
            </div>
            <div class="menu-item">
              <FileText :size="20" class="menu-icon" />
              <span class="menu-text">草稿</span>
            </div>
            <div class="menu-item">
              <Trophy :size="20" class="menu-icon" />
              <div class="menu-text-group">
                <span class="menu-text">成就</span>
                <span class="sub-text blue-text">已解锁 5 个</span>
              </div>
            </div>
            <div class="menu-item">
              <DollarSign :size="20" class="menu-icon" />
              <div class="menu-text-group">
                <span class="menu-text">创收</span>
                <span class="sub-text">在 Reddit 上赚取现金</span>
              </div>
            </div>
          </div>

          <!-- 第三部分：Premium 与设置 -->
          <div class="menu-section">
             <div class="menu-item">
              <Shield :size="20" class="menu-icon" />
              <span class="menu-text">Premium</span>
              <Star :size="16" class="badge-icon" />
            </div>
            <div class="menu-item toggle-item" @click.stop="isDarkMode = !isDarkMode">
              <div class="left-content">
                <Moon :size="20" class="menu-icon" />
                <span class="menu-text">深色模式</span>
              </div>
              <!-- 模拟开关 Switch -->
              <div class="toggle-switch" :class="{ active: isDarkMode }">
                <div class="toggle-circle"></div>
              </div>
            </div>
          </div>

          <div class="divider-line"></div>

          <!-- 第四部分：底部链接 -->
          <div class="menu-section">
             <div class="menu-item">
              <Megaphone :size="20" class="menu-icon" />
              <span class="menu-text">在 Reddit 上投放广告</span>
            </div>
             <div class="menu-item">
              <Clock :size="20" class="menu-icon" />
              <div class="menu-text-group">
                <span class="menu-text">试用 Reddit Pro</span>
                <span class="sub-text orange-text">测试版</span>
              </div>
            </div>
          </div>

          <div class="divider-line"></div>

           <div class="menu-section">
             <div class="menu-item">
              <Settings :size="20" class="menu-icon" />
              <span class="menu-text">设置</span>
            </div>
           </div>

          <div class="divider-line"></div>

          <!-- 退出登录 -->
          <div class="menu-section">
            <div class="menu-item" @click="handleLogout">
              <LogOut :size="20" class="menu-icon" />
              <span class="menu-text">退出登录</span>
            </div>
          </div>

        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
/* --- 全局容器样式 --- */
.header-container {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 2000;
  border-bottom: 1px solid #edeff1;
  gap: 12px;
}

/* --- 汉堡菜单按钮 --- */
.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  color: #1c1c1c;
  transition: background 0.2s;
  flex-shrink: 0;
}

.mobile-menu-btn:hover {
  background: #f6f7f8;
}

/* --- Logo & Search --- */
.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo-section:hover {
  opacity: 0.8;
}

.logo-img {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  transition: transform 0.2s;
}

.logo-section:hover .logo-img {
  transform: scale(1.05);
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #1c1c1c;
  letter-spacing: -0.5px;
}

.search-section {
  flex: 1;
  max-width: 640px;
  margin: 0 24px;
  position: relative;
}

.search-wrapper { position: relative; }
.search-wrapper.is-active .search-bar {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #0079d3;
  background: #fff;
}

.search-bar {
  background: #f6f7f8;
  border-radius: 24px;
  padding: 0 16px;
  height: 40px;
  display: flex;
  align-items: center;
  border: 1px solid transparent;
  position: relative;
  z-index: 1002;
  transition: all 0.2s ease;
}

.search-bar:hover {
  background: #fff;
  border-color: #0079d3;
}

.search-icon {
  color: #878a8c;
  flex-shrink: 0;
}

.search-bar input {
  border: none;
  background: transparent;
  width: 100%;
  margin: 0 10px;
  outline: none;
  font-size: 14px;
}

.clear-icon {
  color: #878a8c;
  cursor: pointer;
  flex-shrink: 0;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s;
}

.clear-icon:hover {
  color: #1c1c1c;
  background: #f6f7f8;
}

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #edeff1;
  border-top: none;
  border-bottom-left-radius: 24px;
  border-bottom-right-radius: 24px;
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
  z-index: 1001;
  padding-bottom: 12px;
}

.dropdown-header {
  padding: 12px 20px 8px;
  font-size: 12px;
  font-weight: 700;
  color: #878a8c;
  display: flex;
  align-items: center;
  gap: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.trending-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  gap: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.trending-item:hover {
  background-color: #f6f7f8;
}

.trend-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.trend-title {
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
}

.trend-desc {
  font-size: 12px;
  color: #787c7e;
  margin-top: 2px;
}

/* --- 右侧功能区 & 头像菜单 --- */
.actions-section {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #1c1c1c;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
  min-width: 40px;
  height: 40px;
}

.btn-icon:hover {
  background: #f6f7f8;
}

/* 头像触发器 */
.user-menu-container {
  position: relative;
}

.avatar-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px;
  border-radius: 8px;
  transition: background 0.2s;
}

.avatar-trigger:hover {
  background: #f6f7f8;
}

.avatar-box {
  position: relative;
  width: 32px;
  height: 32px;
}

.avatar-img-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.user-avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  object-fit: cover;
  background: #ddd;
}

.status-dot {
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 10px;
  height: 10px;
  background: #46d160;
  border: 2px solid #fff;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.dropdown-arrow {
  color: #878a8c;
  display: flex;
  align-items: center;
}

/* --- 个人下拉菜单样式核心 --- */
.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  max-height: calc(100vh - 80px);
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
}

/* 菜单项布局 */
.menu-section {
  display: flex;
  flex-direction: column;
}

/* 用户信息特有样式 */
.menu-item-user {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 12px;
  cursor: pointer;
  color: #1c1c1c;
  border-radius: 8px;
  transition: background 0.15s;
}

.menu-item-user:hover {
  background: #f6f7f8;
}

.user-avatar-large {
  position: relative;
  width: 48px;
  height: 48px;
}

.user-avatar-large img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  background: #ddd;
}

.status-dot.large {
  width: 12px;
  height: 12px;
  right: 0;
  bottom: 0;
  border: 2.5px solid #fff;
}

.user-text-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.user-display-name {
  font-size: 15px;
  font-weight: 600;
  color: #1c1c1c;
}

.user-handle {
  font-size: 13px;
  color: #787c7e;
  margin-top: 2px;
}

/* 通用列表项样式 */
.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  gap: 12px;
  color: #1c1c1c;
  border-radius: 8px;
  transition: background 0.15s;
  margin: 0 4px;
}

.menu-item:hover {
  background: #f6f7f8;
}

.menu-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1c1c1c;
  flex-shrink: 0;
}

.menu-text-group {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.menu-text {
  font-size: 14px;
  font-weight: 500;
}

.sub-text {
  font-size: 12px;
  color: #787c7e;
  margin-top: 2px;
}

.sub-text.blue-text {
  color: #24a0ed;
}

.sub-text.orange-text {
  color: #ff4500;
  font-weight: 600;
}

/* 开关样式 */
.toggle-item {
  justify-content: space-between;
}

.left-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.toggle-switch {
  width: 44px;
  height: 24px;
  background: #edeff1;
  border-radius: 12px;
  position: relative;
  transition: background 0.3s;
  cursor: pointer;
  flex-shrink: 0;
}

.toggle-switch.active {
  background: #0079d3;
}

.toggle-circle {
  width: 20px;
  height: 20px;
  background: #fff;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.3s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.toggle-switch.active .toggle-circle {
  transform: translateX(20px);
}

/* 分割线 */
.divider-line {
  height: 1px;
  background: #edeff1;
  margin: 8px 0;
  width: 100%;
}

.badge-icon {
  margin-left: auto;
  color: #ff4500;
  display: flex;
  align-items: center;
}

/* === 响应式断点 === */

/* 小窗口 (< 640px) */
@media (max-width: 639px) {
  .header-container {
    padding: 0 16px;
  }

  .mobile-menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .logo-text {
    display: none;
  }

  .search-section {
    margin: 0 8px;
    max-width: none;
  }

  .search-bar input {
    font-size: 14px;
  }

  .btn-icon {
    min-width: 36px;
    height: 36px;
    padding: 6px;
  }

  .btn-icon span {
    display: none;
  }

  .profile-dropdown {
    width: calc(100vw - 32px);
    right: -8px;
  }
}

/* 中小窗口 (640px - 767px) */
@media (min-width: 640px) and (max-width: 767px) {
  .mobile-menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .logo-text {
    display: none;
  }

  .search-section {
    margin: 0 12px;
    max-width: 300px;
  }

  .btn-icon span {
    display: none;
  }
}

/* 中等窗口 (768px - 959px) */
@media (min-width: 768px) and (max-width: 959px) {
  .mobile-menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .logo-text {
    display: block;
  }

  .search-section {
    max-width: 400px;
  }

  .btn-icon span {
    display: none;
  }
}

/* 大窗口 (960px - 1023px) */
@media (min-width: 960px) and (max-width: 1023px) {
  .logo-text {
    display: none;
  }

  .search-section {
    max-width: 400px;
  }
}

/* 大窗口及以上 (>= 1024px) */
@media (min-width: 1024px) and (max-width: 1279px) {
  .logo-text {
    display: block;
  }

  .search-section {
    max-width: 500px;
  }
}

/* 超大窗口 (>= 1280px) */
@media (min-width: 1280px) {
  .logo-text {
    display: block;
  }

  .search-section {
    max-width: 640px;
  }
}
</style>