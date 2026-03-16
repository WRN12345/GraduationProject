<script setup lang="ts">
import { useRouter } from 'vue-router'
import { TrendingUp, Award, Users, FileText } from 'lucide-vue-next'
import type { HotCommunity } from '@/composables/useTrending'

defineProps({
  communities: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()

// 跳转到社区详情
const goToCommunity = (communityId) => {
  router.push(`/community/${communityId}`)
}

// 截断描述文本
const truncateDescription = (description, maxLength = 60) => {
  if (!description) return '暂无描述'
  return description.length > maxLength
    ? description.substring(0, maxLength) + '...'
    : description
}

// 格式化数字
const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}
</script>

<template>
  <div class="hot-communities-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="communities.length === 0" class="empty-state">
      <p>暂无热门社区</p>
    </div>

    <!-- 列表内容 -->
    <div v-else class="communities-list">
      <div
        v-for="(community, index) in communities"
        :key="community.id"
        class="hot-community-item"
        @click="goToCommunity(community.id)"
      >
        <!-- 排名 -->
        <span class="rank" :class="{ 'top-three': index < 3 }">
          <Award v-if="index === 0" :size="20" class="medal gold" />
          <Award v-else-if="index === 1" :size="20" class="medal silver" />
          <Award v-else-if="index === 2" :size="20" class="medal bronze" />
          <span v-else class="number">{{ index + 1 }}</span>
        </span>

        <!-- 社区信息 -->
        <div class="community-info">
          <h3 class="community-name">{{ community.name }}</h3>
          <p class="community-description">{{ truncateDescription(community.description) }}</p>
          <div class="community-meta">
            <span class="meta-item">
              <Users :size="11" class="icon" />
              <span>{{ formatNumber(community.member_count) }}</span>
            </span>
            <span class="separator">·</span>
            <span class="meta-item">
              <FileText :size="11" class="icon" />
              <span>{{ formatNumber(community.post_count) }}</span>
            </span>
          </div>
        </div>

        <!-- 热度分数 -->
        <div class="hot-score">
          <TrendingUp :size="14" class="fire-icon" />
          <span class="score">{{ community.hot_rank.toFixed(1) }}</span>
        </div>
      </div>
    </div>
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
  gap: 12px;
  padding: 12px;
  background-color: #ffffff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hot-community-item:hover {
  background-color: #f6f7f8;
  border-color: #d3d6da;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* 排名 */
.rank {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  font-weight: 700;
  font-size: 14px;
}

.rank .medal {
  display: flex;
  align-items: center;
  justify-content: center;
}

.rank .medal.gold {
  color: #ffd700;
}

.rank .medal.silver {
  color: #c0c0c0;
}

.rank .medal.bronze {
  color: #cd7f32;
}

.rank .number {
  color: #878a8c;
}

.rank.top-three .number {
  color: #1c1c1c;
}

/* 社区信息 */
.community-info {
  flex: 1;
  min-width: 0;
}

.community-name {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
  line-height: 1.4;
}

.community-description {
  margin: 0 0 6px 0;
  font-size: 12px;
  color: #878a8c;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.community-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #878a8c;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 2px;
}

.meta-item .icon {
  font-size: 11px;
}

.separator {
  color: #878a8c;
}

/* 热度分数 */
.hot-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 48px;
  padding: 4px 8px;
  background: linear-gradient(135deg, #B5EAD7 0%, #C5E3F6 100%);
  border-radius: 6px;
  color: #ffffff;
}

.fire-icon {
  font-size: 14px;
  line-height: 1;
  color: #1c1c1c;
}

.score {
  font-size: 12px;
  font-weight: 700;
  line-height: 1.2;
  color: #1c1c1c;
}

/* 响应式 */
@media (max-width: 639px) {
  .hot-community-item {
    padding: 10px;
    gap: 8px;
  }

  .community-name {
    font-size: 13px;
  }

  .community-description {
    font-size: 11px;
  }

  .community-meta {
    font-size: 11px;
  }

  .hot-score {
    min-width: 40px;
    color: #1c1c1c;
  }

  .fire-icon {
    font-size: 12px;
  }

  .score {
    font-size: 11px;
  }
}
</style>
