<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search,
  MessageCircle,
  Plus,
  Bell,
  X,
  Shirt,
  FileText,
  LogOut,
  Settings,
  ChevronDown,
  Menu,
  Building2,
  Lock
} from 'lucide-vue-next'
import { useUserStore } from '@/stores/user'
import ProfileEditDialog from '@/components/user/ProfileEditDialog.vue'
import PasswordEditDialog from '@/components/user/PasswordEditDialog.vue'
import SearchSuggestions from '@/components/search/SearchSuggestions.vue'
import { useSearch } from '@/composables/useSearch'
import defaultAvatar from '@/assets/image/wrn.png'

// 默认头像
const DEFAULT_AVATAR = defaultAvatar

// 定义 emit
const emit = defineEmits(['open-mobile-sidebar'])

// 路由
const router = useRouter()

// --- 搜索相关逻辑 ---
const searchText = ref('')
const isSearchFocused = ref(false)

// 使用搜索 composable
const {
  suggestionPosts,
  suggestionUsers,
  suggestionsLoading,
  debouncedFetchSuggestions,
  clearSuggestions,
  hotPosts,
  hotUsers,
  hotLoading,
  fetchHotContent,
  clearHotContent
} = useSearch()

// 监听搜索文本变化，触发搜索建议
watch(searchText, (newVal) => {
  if (newVal && newVal.trim().length >= 1 && isSearchFocused.value) {
    // 有搜索词时，显示搜索建议
    debouncedFetchSuggestions(newVal)
  } else {
    // 搜索框为空时，清除搜索建议
    clearSuggestions()
  }
})

// 搜索框失去焦点
const handleSearchBlur = () => {
  setTimeout(() => { isSearchFocused.value = false }, 200)
}

// 搜索框获得焦点
const handleSearchFocus = () => {
  isSearchFocused.value = true

  // 如果有搜索词，触发搜索建议
  if (searchText.value && searchText.value.trim().length >= 1) {
    debouncedFetchSuggestions(searchText.value)
  } else {
    // 搜索框为空，加载热搜内容
    fetchHotContent(5)
  }
}

// 按 Enter 键搜索
const handleSearchKeydown = (event) => {
  if (event.key === 'Enter' && searchText.value && searchText.value.trim().length >= 1) {
    isSearchFocused.value = false
    router.push({ path: '/search', query: { q: searchText.value.trim() } })
  }
}

// 清除搜索
const clearSearch = () => {
  searchText.value = ''
  clearSuggestions()
}

// 选择搜索建议
const handleSuggestionSelect = () => {
  isSearchFocused.value = false
  clearSuggestions()
}

// --- 个人菜单相关逻辑  ---
const isProfileOpen = ref(false)
const profileEditVisible = ref(false)
const passwordEditVisible = ref(false)

// 获取用户信息
const userInfo = computed(() => userStore.userInfo)

// --- 创建菜单相关逻辑 ---
const isCreateMenuOpen = ref(false)

const toggleProfile = () => {
  isProfileOpen.value = !isProfileOpen.value
  // 如果打开了个人菜单，关闭搜索下拉和创建菜单
  if (isProfileOpen.value) {
    isSearchFocused.value = false
    isCreateMenuOpen.value = false
  }
}

const toggleCreateMenu = () => {
  isCreateMenuOpen.value = !isCreateMenuOpen.value
  // 如果打开了创建菜单，关闭搜索下拉和个人菜单
  if (isCreateMenuOpen.value) {
    isSearchFocused.value = false
    isProfileOpen.value = false
  }
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event) => {
  // 如果点击的不是下拉菜单内部的元素，则关闭所有菜单
  if (isCreateMenuOpen.value || isProfileOpen.value) {
    // 检查点击是否在 create-menu-container 或 user-menu-container 内部
    const createMenu = event.target.closest('.create-menu-container')
    const profileMenu = event.target.closest('.user-menu-container')

    if (!createMenu && !profileMenu) {
      isCreateMenuOpen.value = false
      isProfileOpen.value = false
    }
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

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
  isCreateMenuOpen.value = false
  router.push('/create-post')
}

// 创建社区
const goToCreateCommunity = () => {
  isCreateMenuOpen.value = false
  router.push('/create-community')
}

// 返回主页
const goToHome = () => {
  router.push('/')
}

// 打开个人资料编辑
const openProfileEdit = () => {
  isProfileOpen.value = false
  profileEditVisible.value = true
}

// 打开密码修改
const openPasswordEdit = () => {
  isProfileOpen.value = false
  passwordEditVisible.value = true
}

// 跳转到设置页面
const goToSettings = () => {
  isProfileOpen.value = false
  router.push('/settings')
}

// 查看个人资料
const goToProfile = () => {
  isProfileOpen.value = false
  const username = userInfo.value?.username || userStore.userId
  router.push(`/user/${username}`)
}

// 资料更新成功回调
const handleProfileUpdate = async () => {
  // 重新获取用户信息
  await userStore.fetchUserInfo()
}

// 密码修改成功回调
const handlePasswordUpdate = async () => {
  // 密码修改成功后登出
  await userStore.logout()
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
            @focus="handleSearchFocus"
            @blur="handleSearchBlur"
            @keydown="handleSearchKeydown"
          />
          <X v-if="searchText" :size="16" class="clear-icon" @click="clearSearch" />
        </div>
        <!-- 搜索建议下拉 -->
        <SearchSuggestions
          v-if="isSearchFocused"
          :posts="suggestionPosts"
          :users="suggestionUsers"
          :loading="suggestionsLoading"
          :query="searchText"
          :hotPosts="hotPosts"
          :hotUsers="hotUsers"
          :hotLoading="hotLoading"
          :showHot="!searchText"
          @select="handleSuggestionSelect"
          @close="isSearchFocused = false"
        />
      </div>
    </div>

    <!-- 3. 右侧功能区 -->
    <div class="actions-section">
      <button class="btn-icon" title="消息"><MessageCircle :size="20" /></button>
      <div class="create-menu-container">
        <button
          class="btn-icon"
          :class="{ active: isCreateMenuOpen }"
          title="创建"
          @click="toggleCreateMenu"
        >
          <Plus :size="20" /><span>创建</span>
        </button>

        <!-- 创建下拉菜单 -->
        <div class="create-dropdown" v-if="isCreateMenuOpen">
          <div class="create-menu-item" @click="goToCreatePost">
            <FileText :size="20" class="menu-icon" />
            <span class="menu-text">创建帖子</span>
          </div>
          <div class="create-menu-item" @click="goToCreateCommunity">
            <Building2 :size="20" class="menu-icon" />
            <span class="menu-text">创建社区</span>
          </div>
        </div>
      </div>
      <button class="btn-icon" title="通知"><Bell :size="20" /></button>

      <!-- 个人头像容器 (Dropdown Trigger) -->
      <div class="user-menu-container">
        <div class="avatar-trigger" @click="toggleProfile">
          <div class="avatar-box">
             <div class="avatar-img-wrapper">
               <img :src="userInfo?.avatar || DEFAULT_AVATAR" class="user-avatar-img" />
               <div class="status-dot"></div>
             </div>
          </div>
          <ChevronDown :size="12" class="dropdown-arrow" />
        </div>

        <!-- 个人下拉菜单 (简化版) -->
        <div class="profile-dropdown" v-if="isProfileOpen">
          <!-- 用户信息 -->
          <div class="menu-section user-info-section" @click="goToProfile">
            <div class="menu-item-user">
              <div class="user-avatar-large">
                <img :src="userInfo?.avatar || DEFAULT_AVATAR" />
                <div class="status-dot large"></div>
              </div>
              <div class="user-text-info">
                <div class="user-display-name">{{ userInfo?.nickname || '查看个人资料' }}</div>
                <div class="user-handle">@{{ userInfo?.username || 'user' }}</div>
              </div>
            </div>
          </div>

          <div class="divider-line"></div>

          <!-- 操作菜单 -->
          <div class="menu-section">
            <div class="menu-item" @click="openProfileEdit">
              <Shirt :size="20" class="menu-icon" />
              <span class="menu-text">编辑资料</span>
            </div>
            <div class="menu-item" @click="openPasswordEdit">
              <Lock :size="20" class="menu-icon" />
              <span class="menu-text">修改密码</span>
            </div>
            <div class="menu-item" @click="goToSettings">
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

        <!-- 编辑弹窗 -->
        <ProfileEditDialog
          v-model="profileEditVisible"
          :user="userInfo"
          @success="handleProfileUpdate"
        />
        <PasswordEditDialog
          v-model="passwordEditVisible"
          @success="handlePasswordUpdate"
        />
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

.btn-icon.active {
  background: #f6f7f8;
}

/* 创建菜单容器 */
.create-menu-container {
  position: relative;
}

/* 创建下拉菜单样式 */
.create-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 200px;
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 1003;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.create-menu-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  gap: 12px;
  color: #1c1c1c;
  border-radius: 6px;
  transition: background 0.15s;
}

.create-menu-item:hover {
  background: #f6f7f8;
}

.create-menu-item .menu-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1c1c1c;
  flex-shrink: 0;
}

.create-menu-item .menu-text {
  font-size: 14px;
  font-weight: 500;
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