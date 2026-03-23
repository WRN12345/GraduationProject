<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Award, Users } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import type { HotPost } from '@/composables/useTrending'

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

// 获取热度颜色（基于排名位置）
const getHotColor = (index: number) => {
  // 根据排名分配颜色：前3名用红色系，4-10名用橙色系，其他用蓝色系
  if (index === 0) return rainbowColors[0] // 红 - 第1名
  if (index === 1) return rainbowColors[1] // 橙 - 第2名
  if (index === 2) return rainbowColors[2] // 黄 - 第3名
  if (index < 10) return rainbowColors[3] // 绿 - 4-10名
  return rainbowColors[5] // 蓝 - 其他
}

// 热度等级计算（基于排名位置）
const getHotLevel = (index: number) => {
  // 根据排名来判断热度等级，而不是百分比
  if (index === 0) return { label: '极热', color: '#ff0000' }
  if (index === 1) return { label: '极热', color: '#ff0000' }
  if (index === 2) return { label: '热门', color: '#ff7f00' }
  if (index < 10) return { label: '上升', color: '#00ff00' }
  return { label: '普通', color: '#0000ff' }
}

// 计算最大热度值（用于进度条宽度）
const maxHotRank = computed(() => {
  const ranks = props.posts?.map(p => p.hot_rank) || [100]
  const max = Math.max(...ranks)
  // 如果最大值为负数或0，使用一个小的正数作为基准
  return max > 0 ? max : 1
})

// 获取热度百分比（用于进度条显示）
const getHotPercentage = (hotRank: number) => {
  if (!maxHotRank.value) return 0
  // 确保百分比在 0-100 之间
  return Math.max(0, Math.min(100, (hotRank / maxHotRank.value) * 100))
}

// 格式化时间
const formatTime = (dateString: string | undefined) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  const now = new Date()
  const diff = (now.getTime() - date.getTime()) / 1000 // 秒

  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  if (diff < 604800) return `${Math.floor(diff / 86400)} 天前`

  return date.toLocaleDateString('zh-CN')
}

// 跳转到帖子详情
const goToPost = (postId: number) => {
  router.push(`/post/${postId}`)
}

// Tooltip 状态
const props = defineProps<{
  posts: HotPost[]
  loading?: boolean
}>()

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

const getTooltipData = (post: HotPost, index: number) => {
  const level = getHotLevel(index)
  return {
    value: post.hot_rank.toFixed(1),
    level: level.label,
    color: level.color
  }
}
</script>

<template>
  <div class="hot-posts-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="posts.length === 0" class="empty-state">
      <p>暂无热门帖子</p>
    </div>

    <!-- 列表内容 -->
    <div v-else class="posts-list">
      <div
        v-for="(post, index) in posts"
        :key="post.id"
        class="hot-post-item"
        @click="goToPost(post.id)"
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

        <!-- 中间内容区 -->
        <div class="content-section">
          <!-- 标题 -->
          <h3 class="post-title">{{ post.title }}</h3>
          
          <!-- 摘要/标签行 -->
          <div class="post-tags">
            <span class="tag community-tag">
              <Users :size="10" />
              {{ post.community_name }}
            </span>
            <span class="tag author-tag">
              {{ post.author_username }}
            </span>
            <span class="time-tag">{{ formatTime(post.created_at) }}</span>
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
                width: `${getHotPercentage(post.hot_rank)}%`,
                backgroundColor: getHotColor(index)
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
        <div class="tooltip-value">{{ getTooltipData(posts[hoveredIndex], hoveredIndex).value }}</div>
        <div 
          class="tooltip-level"
          :style="{ color: getTooltipData(posts[hoveredIndex], hoveredIndex).color }"
        >
          {{ getTooltipData(posts[hoveredIndex], hoveredIndex).level }}
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.hot-posts-list {
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
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hot-post-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background-color: #ffffff;
  border: 1px solid #edeff1;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hot-post-item:hover {
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
  min-width: 36px;
  height: 36px;
}

.medal-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
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
  font-size: 16px;
  font-weight: 700;
  color: #b0b0b0;
}

/* 内容区域 */
.content-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.post-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 标签行 */
.post-tags {
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
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.community-tag {
  background-color: #e3f2fd;
  color: #1976d2;
}

.author-tag {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.time-tag {
  font-size: 11px;
  color: #9e9e9e;
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
  .hot-post-item {
    padding: 10px 12px;
    gap: 10px;
  }

  .rank-section {
    min-width: 28px;
    height: 28px;
  }

  .medal-badge {
    width: 26px;
    height: 26px;
  }

  .medal-badge :deep(svg) {
    width: 12px;
    height: 12px;
  }

  .rank-number {
    font-size: 14px;
  }

  .post-title {
    font-size: 13px;
  }

  .hot-progress-container {
    width: 48px;
  }
}
</style>
