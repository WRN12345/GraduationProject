<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// --- 搜索相关逻辑 (保留之前的) ---
const searchText = ref('')
const isSearchFocused = ref(false)
const trendingList = ref([
  { id: 1, title: 'TGA 2025 Winners', desc: '年度游戏大奖公布', icon: '🏆' },
  { id: 2, title: 'Vue.js 3.5 Release', desc: '前端框架新版本', icon: '🟢' },
  { id: 3, title: 'GTA VI Leak', desc: '侠盗猎车手6最新泄露', icon: '🎮' },
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

// 点击外部关闭菜单 (简单的实现)
const closeProfile = (e) => {
  // 这里简单处理，实际项目中通常使用 vueuse 的 onClickOutside
  // 为了不破坏组件内点击，这里暂时依靠 toggle，
  // 生产环境建议添加 window 监听器判断点击目标是否在菜单外
}

</script>

<template>
  <header class="header-container">
    <!-- 1. Logo 区域 -->
    <div class="logo-section">
      <img src="@/assets/image/wrn.png" alt="Logo" class="logo-img" />
      <span class="logo-text">Super Dev</span>
    </div>

    <!-- 2. 搜索框区域 -->
    <div class="search-section">
      <div class="search-wrapper" :class="{ 'is-active': isSearchFocused }">
        <div class="search-bar">
          <span class="search-icon">🔍</span>
          <input 
            type="text" 
            placeholder="查找所需一切信息" 
            v-model="searchText"
            @focus="isSearchFocused = true"
            @blur="handleSearchBlur"
          />
          <span v-if="searchText" class="clear-icon" @click="searchText = ''">✕</span>
        </div>
        <!-- 搜索下拉 (保留之前的代码) -->
        <div class="search-dropdown" v-if="isSearchFocused">
          <div class="dropdown-header"><span>🔥 热门趋势</span></div>
          <ul class="trending-list">
            <li v-for="item in trendingList" :key="item.id" class="trending-item" @click="handleSearchResultSelect(item)">
              <div class="trend-icon">{{ item.icon }}</div>
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
      <button class="btn-icon">💬</button>
      <button class="btn-icon">➕ 创建</button>
      <button class="btn-icon">🔔</button>
      
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
          <span class="dropdown-arrow">▼</span>
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
              <span class="menu-icon">👕</span>
              <span class="menu-text">编辑头像</span>
            </div>
            <div class="menu-item">
              <span class="menu-icon">📄</span>
              <span class="menu-text">草稿</span>
            </div>
            <div class="menu-item">
              <span class="menu-icon">🏆</span>
              <div class="menu-text-group">
                <span class="menu-text">成就</span>
                <span class="sub-text blue-text">已解锁 5 个</span>
              </div>
            </div>
            <div class="menu-item">
              <span class="menu-icon">💲</span>
              <div class="menu-text-group">
                <span class="menu-text">创收</span>
                <span class="sub-text">在 Reddit 上赚取现金</span>
              </div>
            </div>
          </div>

          <!-- 第三部分：Premium 与设置 -->
          <div class="menu-section">
             <div class="menu-item">
              <span class="menu-icon">🛡️</span>
              <span class="menu-text">Premium</span>
              <span class="badge-icon">🦄</span>
            </div>
            <div class="menu-item toggle-item" @click.stop="isDarkMode = !isDarkMode">
              <div class="left-content">
                <span class="menu-icon">🌙</span>
                <span class="menu-text">深色模式</span>
              </div>
              <!-- 模拟开关 Switch -->
              <div class="toggle-switch" :class="{ active: isDarkMode }">
                <div class="toggle-circle"></div>
              </div>
            </div>
            <div class="menu-item">
              <span class="menu-icon">🚪</span>
              <span class="menu-text">注销</span>
            </div>
          </div>
          
          <div class="divider-line"></div>

          <!-- 第四部分：底部链接 -->
          <div class="menu-section">
             <div class="menu-item">
              <span class="menu-icon">📢</span>
              <span class="menu-text">在 Reddit 上投放广告</span>
            </div>
             <div class="menu-item">
              <span class="menu-icon">🕒</span>
              <div class="menu-text-group">
                <span class="menu-text">试用 Reddit Pro</span>
                <span class="sub-text orange-text">测试版</span>
              </div>
            </div>
          </div>

          <div class="divider-line"></div>

           <div class="menu-section">
             <div class="menu-item">
              <span class="menu-icon">⚙️</span>
              <span class="menu-text">设置</span>
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
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: #fff;
  position: relative;
  z-index: 2000;
}

/* --- Logo & Search (保持原样) --- */
.logo-section { display: flex; align-items: center; gap: 8px; width: 260px; }
.logo-img { width: 32px; height: 32px; border-radius: 50%; }
.logo-text { font-size: 20px; font-weight: bold; }

.search-section { flex: 1; max-width: 600px; position: relative; }
.search-wrapper { position: relative; }
.search-wrapper.is-active .search-bar { border-bottom-left-radius: 0; border-bottom-right-radius: 0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border-color: #0079d3; background: #fff; }
.search-bar { background: #f6f7f8; border-radius: 20px; padding: 0 15px; height: 40px; display: flex; align-items: center; border: 1px solid transparent; position: relative; z-index: 1002; transition: all 0.2s; }
.search-bar:hover { background: #fff; border: 1px solid #0079d3; }
.search-bar input { border: none; background: transparent; width: 100%; margin-left: 10px; outline: none; }
.search-dropdown { position: absolute; top: 100%; left: 0; right: 0; background: #fff; border: 1px solid #edeff1; border-top: none; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); z-index: 1001; padding-bottom: 10px; }
.dropdown-header { padding: 12px 16px 8px; font-size: 12px; font-weight: 700; color: #878a8c; }
.trending-item { display: flex; align-items: center; padding: 8px 16px; gap: 12px; cursor: pointer; }
.trending-item:hover { background-color: #f6f7f8; }
.trend-icon { width: 32px; height: 32px; background: #f0f0f0; border-radius: 4px; display: flex; align-items: center; justify-content: center; } 
.trend-title { font-size: 14px; font-weight: 500; } .trend-desc { font-size: 12px; color: #787c7e; }

/* --- 右侧功能区 & 头像菜单 --- */
.actions-section { display: flex; align-items: center; gap: 15px; width: 260px; justify-content: flex-end; }
.btn-icon { background: none; border: none; cursor: pointer; font-size: 16px; font-weight: 600; display: flex; align-items: center; gap: 5px; }

/* 头像触发器 */
.user-menu-container { position: relative; }
.avatar-trigger {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
}
.avatar-trigger:hover { background: #f6f7f8; }

.avatar-box { position: relative; width: 30px; height: 30px; }
.avatar-img-wrapper { position: relative; width: 100%; height: 100%; }
.user-avatar-img { width: 100%; height: 100%; border-radius: 4px; object-fit: cover; background: #ddd; }
.status-dot {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 8px;
  height: 8px;
  background: #46d160; /* 在线绿 */
  border: 2px solid #fff;
  border-radius: 50%;
}
.dropdown-arrow { font-size: 10px; color: #878a8c; }

/* --- 个人下拉菜单样式核心 --- */
.profile-dropdown {
  position: absolute;
  top: 45px;
  right: 0;
  width: 280px;
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  max-height: calc(100vh - 60px);
  overflow-y: auto;
  padding: 8px 0;
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
  padding: 10px 16px;
  gap: 12px;
  cursor: pointer;
  color: #1c1c1c;
}
.menu-item-user:hover { background: #f6f7f8; }
.user-avatar-large { position: relative; width: 40px; height: 40px; }
.user-avatar-large img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; background: #ddd; }
.status-dot.large { width: 10px; height: 10px; right: 0; bottom: 0; border: 2px solid #fff; }

.user-text-info { display: flex; flex-direction: column; }
.user-display-name { font-size: 14px; font-weight: 500; color: #1c1c1c; }
.user-handle { font-size: 12px; color: #787c7e; }

/* 通用列表项样式 */
.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  gap: 12px;
  color: #1c1c1c;
}
.menu-item:hover { background: #f6f7f8; }

.menu-icon {
  width: 20px;
  height: 20px;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1c1c1c;
}

.menu-text-group { display: flex; flex-direction: column; }
.menu-text { font-size: 14px; font-weight: 500; }

.sub-text { font-size: 12px; color: #787c7e; margin-top: 2px; }
.sub-text.blue-text { color: #24a0ed; }
.sub-text.orange-text { color: #ff4500; font-weight: bold; }

/* 开关样式 */
.toggle-item { justify-content: space-between; }
.left-content { display: flex; align-items: center; gap: 12px; }

.toggle-switch {
  width: 40px;
  height: 24px;
  background: #edeff1;
  border-radius: 12px;
  position: relative;
  transition: background 0.3s;
}
.toggle-switch.active { background: #0079d3; }
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
.toggle-switch.active .toggle-circle { transform: translateX(16px); }

/* 分割线 */
.divider-line {
  height: 1px;
  background: #edeff1;
  margin: 8px 0;
  width: 100%;
}

.badge-icon { margin-left: auto; font-size: 14px; }
</style>