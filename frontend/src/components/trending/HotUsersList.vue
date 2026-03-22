<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Award, Star, FileText, MessageCircle } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import type { HotUser } from '@/composables/useTrending'

const props = defineProps<{
  users: HotUser[]
  loading?: boolean
}>()

const router = useRouter()

// 彩虹色卡
const rainbowColors = [
  '#ff0000', // 红
  '#ff7f00', // 橙
  '#ffff00', // 黄
  '#00ff00', // 绿
  '#00ffff', // 青
  '#0000ff', // 蓝
  '#8b00ff', // 紫
]

// 根据热度百分比获取彩虹色
const getRainbowColor = (percentage: number) => {
  const index = Math.floor((percentage / 100) * (rainbowColors.length - 1))
  return rainbowColors[Math.min(index, rainbowColors.length - 1)]
}

// 获取热度颜色（彩虹色）
const getHotColor = (hotRank: number, maxRank: number) => {
  const percentage = maxRank > 0 ? (hotRank / maxRank) * 100 : 0
  return getRainbowColor(percentage)
}

// 热度等级计算（保留用于 tooltip）
const getHotLevel = (percentage: number) => {
  if (percentage >= 80) return { label: '极热', color: '#ff0000' }
  if (percentage >= 50) return { label: '热门', color: '#ff7f00' }
  if (percentage >= 20) return { label: '上升', color: '#00ff00' }
  return { label: '普通', color: '#0000ff' }
}

// 计算最大热度值
const maxHotRank = computed(() => {
  const usersArray = props.users || []
  return Math.max(...usersArray.map(u => u.hot_rank), 100)
})

// 获取热度百分比
const getHotPercentage = (hotRank: number) => {
  if (!maxHotRank.value) return 0
  return (hotRank / maxHotRank.value) * 100
}

// 跳转到用户资料
const goToUser = (username: string) => {
  router.push(`/user/${username}`)
}

// 格式化数字
const formatNumber = (num: number) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

// 获取用户显示名称
const getDisplayName = (user: HotUser) => {
  return user.nickname || user.username
}

// 获取用户头像背景色
const getAvatarGradient = (username: string) => {
  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
    'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)'
  ]
  const index = username.charCodeAt(0) % gradients.length
  return gradients[index]
}

// Tooltip 状态
const hoveredIndex = ref<number | null>(null)
const tooltipPosition = ref({ x: 0, y: 0 })

const showTooltip = (event: MouseEvent, index: number) => {
  hoveredIndex.value = index
  const rect = (event.target as HTMLElement).getBoundingClientRect()
  tooltipPosition.value = {
    x: rect.left + rect.width / 2,
    y: rect.top - 10
  }
}

const hideTooltip = () => {
  hoveredIndex.value = null
}

const getTooltipData = (user: HotUser) => {
  const percentage = getHotPercentage(user.hot_rank)
  const level = getHotLevel(percentage)
  return {
    value: user.hot_rank.toFixed(1),
    level: level.label,
    color: level.color
  }
}
</script>

<template>
  <div class="hot-users-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="users.length === 0" class="empty-state">
      <p>暂无活跃用户</p>
    </div>

    <!-- 列表内容 -->
    <div v-else class="users-list">
      <div
        v-for="(user, index) in users"
        :key="user.id"
        class="hot-user-item"
        @click="goToUser(user.username)"
      >
        <!-- 排名区域 -->
        <div class="rank-section">
          <!-- 前三名圆形金银铜徽章 -->
          <div v-if="index === 0" class="medal-badge gold">
            <Award :size="16" />
          </div>
          <div v-else-if="index === 1" class="medal-badge silver">
            <Award :size="16" />
          </div>
          <div v-else-if="index === 2" class="medal-badge bronze">
            <Award :size="16" />
          </div>
          <!-- 4-10名淡灰色数字 -->
          <span v-else class="rank-number">{{ index + 1 }}</span>
        </div>

        <!-- 用户头像 -->
        <div class="user-avatar" :style="{ background: getAvatarGradient(user.username) }">
          <img
            v-if="user.avatar"
            :src="user.avatar"
            :alt="user.username"
            class="avatar-image"
          />
          <div v-else class="avatar-placeholder">
            {{ user.username[0].toUpperCase() }}
          </div>
        </div>

        <!-- 中间内容区 -->
        <div class="content-section">
          <!-- 用户名称 -->
          <h3 class="user-username">{{ getDisplayName(user) }}</h3>
          
          <!-- 统计摘要 -->
          <div class="user-tags">
            <span class="tag">
              <FileText :size="10" />
              {{ formatNumber(user.post_count) }}
            </span>
            <span class="tag">
              <MessageCircle :size="10" />
              {{ formatNumber(user.comment_count) }}
            </span>
          </div>
        </div>

        <!-- 热度 Mini Progress Bar -->
        <div 
          class="hot-progress-container"
          @mouseenter="showTooltip($event, index)"
          @mouseleave="hideTooltip"
        >
          <div class="mini-progress-bar">
            <div 
              class="progress-fill" 
              :style="{ 
                width: `${getHotPercentage(user.hot_rank)}%`,
                backgroundColor: getHotColor(user.hot_rank, maxHotRank)
              }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tooltip -->
    <Teleport to="body">
      <div 
        v-if="hoveredIndex !== null" 
        class="tooltip"
        :style="{
          left: `${tooltipPosition.x}px`,
          top: `${tooltipPosition.y}px`
        }"
      >
        <div class="tooltip-value">{{ getTooltipData(users[hoveredIndex]).value }}</div>
        <div 
          class="tooltip-level"
          :style="{ color: getTooltipData(users[hoveredIndex]).color }"
        >
          {{ getTooltipData(users[hoveredIndex]).level }}
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.hot-users-list {
  width: 100%;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #878a8c;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #edeff1;
  border-top-color: #0079d3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  margin-top: 12px;
  font-size: 14px;
}

/* 空状态 */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #878a8c;
  font-size: 14px;
}

/* 列表 */
.users-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hot-user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background-color: #ffffff;
  border: 1px solid #edeff1;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hot-user-item:hover {
  background-color: #fafafa;
  border-color: #d3d6da;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 排名区域 */
.rank-section {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
}

.medal-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

.medal-badge.gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
}

.medal-badge.silver {
  background: linear-gradient(135deg, #e0e0e0 0%, #bdbdbd 100%);
}

.medal-badge.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #a0522d 100%);
}

.rank-number {
  font-size: 14px;
  font-weight: 700;
  color: #b0b0b0;
}

/* 用户头像 */
.user-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
}

/* 内容区域 */
.content-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-username {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 标签行 */
.user-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 6px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 11px;
  color: #616161;
}

/* 热度 Mini Progress Bar */
.hot-progress-container {
  width: 60px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.mini-progress-bar {
  width: 100%;
  height: 6px;
  background-color: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* Tooltip */
.tooltip {
  position: fixed;
  transform: translate(-50%, -100%);
  background-color: #1c1c1c;
  color: #ffffff;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  z-index: 9999;
  pointer-events: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.tooltip::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid #1c1c1c;
}

.tooltip-value {
  font-size: 16px;
  font-weight: 700;
  text-align: center;
}

.tooltip-level {
  font-size: 11px;
  font-weight: 600;
  text-align: center;
  margin-top: 2px;
}

/* 响应式 */
@media (max-width: 639px) {
  .hot-user-item {
    padding: 8px 12px;
    gap: 8px;
  }

  .rank-section {
    min-width: 24px;
    height: 24px;
  }

  .medal-badge {
    width: 22px;
    height: 22px;
  }

  .medal-badge :deep(svg) {
    width: 10px;
    height: 10px;
  }

  .rank-number {
    font-size: 12px;
  }

  .user-avatar {
    width: 32px;
    height: 32px;
  }

  .avatar-placeholder {
    font-size: 12px;
  }

  .user-username {
    font-size: 13px;
  }

  .hot-progress-container {
    width: 48px;
  }
}
</style>
