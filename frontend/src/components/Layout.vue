<script setup>
import { ref } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import Header from './Header.vue'
import Aside from './Aside.vue'

const isSidebarCollapsed = ref(false)
const isMobileSidebarOpen = ref(false)

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const openMobileSidebar = () => {
  isMobileSidebarOpen.value = true
}

const closeMobileSidebar = () => {
  isMobileSidebarOpen.value = false
}
</script>

<template>
  <div class="app-layout">
    <div class="layout-header">
      <Header @open-mobile-sidebar="openMobileSidebar" />
    </div>

    <div class="layout-body">
      <!-- 遮罩层 -->
      <div
        class="sidebar-overlay"
        :class="{ active: isMobileSidebarOpen }"
        @click="closeMobileSidebar"
      ></div>

      <div
        class="layout-aside"
        :class="{
          collapsed: isSidebarCollapsed,
          'mobile-open': isMobileSidebarOpen
        }"
      >
        <div class="aside-content">
          <Aside
            :is-collapsed="isSidebarCollapsed"
            :is-mobile-open="isMobileSidebarOpen"
            @close-mobile="closeMobileSidebar"
          />
        </div>
      </div>

      <button
        class="sidebar-toggle"
        :class="{ 'is-collapsed': isSidebarCollapsed }"
        @click="toggleSidebar"
        :title="isSidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
      >
        <ChevronLeft v-if="!isSidebarCollapsed" :size="20" />
        <ChevronRight v-else :size="20" />
      </button>

      <div class="layout-main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: #ffffff;
  border-bottom: 1px solid #edeff1;
}

.layout-body {
  display: flex;
  align-items: stretch;
  max-width: 100%;
  height: calc(100vh - 56px);
  overflow: hidden;
  position: relative;
}

/* --- 遮罩层 --- */
.sidebar-overlay {
  position: fixed;
  top: 56px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.sidebar-overlay.active {
  opacity: 1;
  visibility: visible;
}

/* --- 侧边栏 --- */
.layout-aside {
  width: 270px;
  display: none;
  padding: 0;
  transition: all 0.3s ease;
  position: sticky;
  top: 0;
  height: calc(100vh - 56px);
  overflow: hidden;
  flex-shrink: 0;
  z-index: 999;
}

.aside-content::-webkit-scrollbar {
  width: 6px;
}

.aside-content::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.aside-content::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.layout-aside.collapsed {
  width: 60px;
}

.aside-content {
  height: calc(100vh - 56px);
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 10px;
}

/* --- 侧边栏收起/展开按钮 --- */
.sidebar-toggle {
  position: absolute;
  left: 270px;
  top: 0;
  width: 36px;
  height: 36px;
  background: #ffffff;
  border: 1px solid #edeff1;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 100;
  padding: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  flex-shrink: 0;
}

.sidebar-toggle.is-collapsed {
  left: 60px;
}

.layout-main {
  flex: 1;
  padding: 0 24px;
  transition: all 0.3s ease;
  height: calc(100vh - 56px);
  overflow-y: auto;
  overflow-x: hidden;
}

.layout-main::-webkit-scrollbar {
  width: 8px;
}

.layout-main::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

.layout-main::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.sidebar-toggle:hover {
  background: #f6f7f8;
  border-color: #0079d3;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

/* === 响应式断点 === */

/* 小窗口 (< 640px) */
@media (max-width: 639px) {
  .layout-aside {
    position: fixed;
    left: -270px;
    width: 270px;
    height: calc(100vh - 56px);
    background: #fff;
    box-shadow: 2px 0 8px rgba(0,0,0,0.15);
  }

  .layout-aside.mobile-open {
    left: 0;
  }

  .sidebar-toggle {
    display: none;
  }

  .layout-main {
    padding: 0 16px;
    max-width: 100%;
  }
}

/* 中小窗口 (640px - 767px) */
@media (min-width: 640px) and (max-width: 767px) {
  .layout-aside {
    position: fixed;
    left: -270px;
    width: 270px;
    height: calc(100vh - 56px);
    background: #fff;
    box-shadow: 2px 0 8px rgba(0,0,0,0.15);
  }

  .layout-aside.mobile-open {
    left: 0;
  }

  .sidebar-toggle {
    display: none;
  }

  .layout-main {
    padding: 0 20px;
  }
}

/* 中等窗口 (768px - 959px) */
@media (min-width: 768px) and (max-width: 959px) {
  .layout-aside {
    display: block;
    position: fixed;
    left: -270px;
    height: calc(100vh - 56px);
    background: #fff;
    box-shadow: 2px 0 8px rgba(0,0,0,0.15);
  }

  .layout-aside.mobile-open {
    left: 0;
  }

  .sidebar-toggle {
    display: none;
  }

  .layout-main {
    padding: 0 20px;
  }
}

/* 大窗口 (960px - 1023px) */
@media (min-width: 960px) and (max-width: 1023px) {
  .layout-aside {
    display: block;
  }

  .layout-aside.collapsed {
    display: block;
  }

  .sidebar-toggle {
    display: flex;
  }

  .layout-main {
    padding: 0 20px;
  }
}

/* 大窗口及以上 (>= 1024px) */
@media (min-width: 1024px) {
  .layout-aside {
    display: block;
  }

  .layout-aside.collapsed {
    display: block;
  }

  .sidebar-toggle {
    display: flex;
  }
}
</style>