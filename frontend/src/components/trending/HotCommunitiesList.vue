<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Award, Users, FileText } from 'lucide-vue-next'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { HotCommunity } from '@/composables/useTrending'

const props = defineProps<{
  communities: HotCommunity[]
  loading?: boolean
}>()

const router = useRouter()
const { t } = useI18n()

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
  if (percentage >= 80) return { label: t('hotPosts.extremelyHot'), color: '#ff0000' }
  if (percentage >= 50) return { label: t('hotPosts.hot'), color: '#ff7f00' }
  if (percentage >= 20) return { label: t('hotPosts.rising'), color: '#00ff00' }
  return { label: t('hotPosts.normal'), color: '#0000ff' }
}

// 计算最大热度值
const maxHotRank = computed(() => {
  const communitiesArray = props.communities || []
  return Math.max(...communitiesArray.map(c => c.hot_rank), 100)
})

// 获取热度百分比
const getHotPercentage = (hotRank: number) => {
  if (!maxHotRank.value) return 0
  return (hotRank / maxHotRank.value) * 100
}

// 跳转到社区详情
const goToCommunity = (communityId: number) => {
  router.push(`/community/${communityId}`)
}

// 截断描述文本
const truncateDescription = (description: string | undefined, maxLength = 50) => {
  if (!description) return t('common.noDescription')
  return description.length > maxLength
    ? description.substring(0, maxLength) + '...'
    : description
}

// 格式化数字
const formatNumber = (num: number) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + t('common.tenThousand')
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
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

const getTooltipData = (community: HotCommunity) => {
  const percentage = getHotPercentage(community.hot_rank)
  const level = getHotLevel(percentage)
  return {
    value: community.hot_rank.toFixed(1),
    level: level.label,
    color: level.color
  }
}
</script>

<template>
  <div class="hot-communities-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('common.loading') }}</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="communities.length === 0" class="empty-state">
      <p>{{ t('hotCommunities.noHotCommunities') }}</p>
    </div>

    <!-- 列表内容 -->
    <div v-else class="communities-list">
      <div
        v-for="(community, index) in communities"
        :key="community.id"
        class="hot-community-item"
        @click="goToCommunity(community.id)"
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
          <!-- 社区名称 -->
          <h3 class="community-name">{{ community.name }}</h3>
          
          <!-- 描述摘要 -->
          <p class="community-description">{{ truncateDescription(community.description) }}</p>
          
          <!-- 标签行 -->
          <div class="community-tags">
            <span class="tag">
              <Users :size="10" />
              {{ formatNumber(community.member_count) }}
            </span>
            <span class="tag">
              <FileText :size="10" />
              {{ formatNumber(community.post_count) }}
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
                width: `${getHotPercentage(community.hot_rank)}%`,
                backgroundColor: getHotColor(community.hot_rank, maxHotRank)
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
        <div class="tooltip-value">{{ getTooltipData(communities[hoveredIndex]).value }}</div>
        <div 
          class="tooltip-level"
          :style="{ color: getTooltipData(communities[hoveredIndex]).color }"
        >
          {{ getTooltipData(communities[hoveredIndex]).level }}
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.hot-communities-list {
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
.communities-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hot-community-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background-color: var(--bg-card);
  border: 1px solid #edeff1;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hot-community-item:hover {
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
  color: var(--text-inverse);
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
  gap: 4px;
}

.community-name {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
  line-height: 1.4;
}

.community-description {
  margin: 0;
  font-size: 12px;
  color: #757575;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

/* 标签行 */
.community-tags {
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
  color: var(--text-inverse);
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
  .hot-community-item {
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

  .community-name {
    font-size: 13px;
  }

  .community-description {
    font-size: 11px;
  }

  .hot-progress-container {
    width: 48px;
  }
}
</style>
