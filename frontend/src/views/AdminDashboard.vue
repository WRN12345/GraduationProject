<script setup>
import { ref, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Users, FileText, MessageSquare, Building2,
  UserX, Trash2, ShieldCheck
} from 'lucide-vue-next'
import StatsCard from '@/components/admin/StatsCard.vue'
import { getDashboardStats, getActionStats, getTrend } from '@/api/admin'
import { useAdminTimeFilter } from '@/composables/useAdminTimeFilter'

// ECharts 按需引入
import { use } from 'echarts/core'
import { PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'

use([
  PieChart, BarChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
  CanvasRenderer
])

const { t } = useI18n()
const { selectedRange, getDaysParam } = useAdminTimeFilter()

// ========== 统计数据 ==========
const loading = ref(true)
const stats = ref({
  total_users: 0, total_posts: 0, total_comments: 0, total_communities: 0,
  today_new_users: 0, today_new_posts: 0, today_new_comments: 0,
  deleted_posts: 0, deleted_comments: 0,
  hard_deleted_posts: 0, hard_deleted_comments: 0,
  admin_users: 0, banned_users: 0
})

// ========== 图表配置 ==========
const chartLoading = ref(true)

// 图表1: 帖子&评论状态分布（饼图）
const statusPieOption = ref({ title: { text: '' }, tooltip: {}, legend: {}, series: [] })

// 图表2: 操作趋势（柱状图）
const trendBarOption = ref({ title: { text: '' }, tooltip: {}, xAxis: {}, yAxis: {}, series: [] })

// 图表3: 用户构成（饼图）
const userPieOption = ref({ title: { text: '' }, tooltip: {}, legend: {}, series: [] })

// 图表4: 操作类型统计（柱状图）
const actionBarOption = ref({ title: { text: '' }, tooltip: {}, xAxis: {}, yAxis: {}, series: [] })

// ========== 数据获取 ==========
async function fetchStats() {
  loading.value = true
  try {
    const data = await getDashboardStats()
    stats.value = data
  } catch (e) {
    console.error('[AdminDashboard] 获取统计数据失败:', e)
  } finally {
    loading.value = false }
}

function buildCharts() {
  const s = stats.value

  // ---- 图表1: 帖子&评论状态分布（环形饼图）----
  const normalPosts = Math.max(0, s.total_posts - s.deleted_posts)
  const normalComments = Math.max(0, s.total_comments - s.deleted_comments)
  statusPieOption.value = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { fontSize: 12 } },
    color: ['#67c23a', '#e6a23c', '#f56c6c', '#909399'],
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: [
        { value: normalPosts, name: t('admin.dashboard.postNormal') || 'Normal Posts' },
        { value: s.deleted_posts, name: t('admin.dashboard.softDeletedPosts') || 'Soft Deleted' },
        { value: s.hard_deleted_posts, name: t('admin.dashboard.hardDeletedPosts') || 'Hard Deleted' },
        { value: normalComments, name: t('admin.dashboard.normalComments') || 'Normal Comments' },
        { value: s.deleted_comments, name: t('admin.dashboard.softDeletedComments') || 'Soft Del Comments' },
        { value: s.hard_deleted_comments, name: t('admin.dashboard.hardDeletedComments') || 'Hard Del Comments' },
      ]
    }]
  }

  // ---- 图表2: 用户构成（饼图）----
  const regularUsers = Math.max(0, s.total_users - s.admin_users - s.banned_users)
  userPieOption.value = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { fontSize: 12 } },
    color: ['#409eff', '#e6a23c', '#f56c6c'],
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: [
        { value: regularUsers, name: t('admin.dashboard.regularUsers') || 'Regular Users' },
        { value: s.admin_users, name: t('admin.dashboard.adminUsers') || 'Admins' },
        { value: s.banned_users, name: t('admin.dashboard.bannedUsers') || 'Banned' },
      ]
    }]
  }

  // 获取图表3和图表4的动态数据
  fetchChartData()
}

async function fetchChartData() {
  chartLoading.value = true
  try {
    // 并行请求趋势和操作统计
    const [trendRes, actionRes] = await Promise.all([
      getTrend(getDaysParam.value || 30),
      getActionStats()
    ])

    // ---- 图表3: 操作趋势（柱状图）----
    const trendDates = trendRes.items.map(i => i.date.slice(5)) // MM-DD
    const trendCounts = trendRes.items.map(i => i.count)
    trendBarOption.value = {
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 16, top: 16, bottom: 36 },
      xAxis: {
        type: 'category',
        data: trendDates,
        axisLabel: { fontSize: 10, rotate: trendDates.length > 15 ? 30 : 0 }
      },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        type: 'bar',
        data: trendCounts,
        itemStyle: { borderRadius: [4, 4, 0, 0], color: '#ff6b35' },
        barMaxWidth: 20
      }]
    }

    // ---- 图表4: 操作类型统计（横向柱状图）----
    // 取前 10 个操作类型
    const topActions = actionRes.items.slice(0, 10)
    actionBarOption.value = {
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: 120, right: 24, top: 16, bottom: 16 },
      xAxis: { type: 'value', minInterval: 1 },
      yAxis: {
        type: 'category',
        data: topActions.map(i => i.action_name).reverse(),
        axisLabel: { fontSize: 11 }
      },
      series: [{
        type: 'bar',
        data: topActions.map(i => i.count).reverse(),
        itemStyle: { borderRadius: [0, 4, 4, 0], color: '#409eff' },
        barMaxWidth: 20
      }]
    }
  } catch (e) {
    console.error('[AdminDashboard] 获取图表数据失败:', e)
  } finally {
    chartLoading.value = false
  }
}

onMounted(async () => {
  await fetchStats()
  buildCharts()
})

watch(selectedRange, () => {
  if (!loading.value) {
    fetchChartData()
  }
})
</script>

<template>
  <div class="admin-dashboard">
    <div class="page-header">
      <h1 class="page-title">{{ t('admin.dashboard.title') }}</h1>
      <p class="page-desc">{{ t('admin.dashboard.description') }}</p>
    </div>

    <!-- 统计卡片 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <span>{{ t('common.loading') }}</span>
    </div>

    <template v-else>
      <!-- 总量统计 -->
      <div class="stats-section">
        <h2 class="section-title">{{ t('admin.dashboard.overview') }}</h2>
        <div class="stats-grid">
          <StatsCard :title="t('admin.dashboard.totalUsers')" :value="stats.total_users"
            :subtitle="t('admin.dashboard.todayNew', { count: stats.today_new_users })" :icon="Users" color="#0079d3" />
          <StatsCard :title="t('admin.dashboard.totalPosts')" :value="stats.total_posts"
            :subtitle="t('admin.dashboard.todayNew', { count: stats.today_new_posts })" :icon="FileText" color="#ff4500" />
          <StatsCard :title="t('admin.dashboard.totalComments')" :value="stats.total_comments"
            :subtitle="t('admin.dashboard.todayNew', { count: stats.today_new_comments })" :icon="MessageSquare" color="#46d160" />
          <StatsCard :title="t('admin.dashboard.totalCommunities')" :value="stats.total_communities" :icon="Building2" color="#ff6b35" />
        </div>
      </div>

      <!-- 管理统计 -->
      <div class="stats-section">
        <h2 class="section-title">{{ t('admin.dashboard.managementStats') }}</h2>
        <div class="stats-grid">
          <StatsCard :title="t('admin.dashboard.adminUsers')" :value="stats.admin_users" :icon="ShieldCheck" color="#ff4500" />
          <StatsCard :title="t('admin.dashboard.bannedUsers')" :value="stats.banned_users" :icon="UserX" color="#ea0027" />
          <StatsCard :title="t('admin.dashboard.deletedPosts')" :value="stats.deleted_posts + stats.hard_deleted_posts" :icon="Trash2" color="#787c7e" />
          <StatsCard :title="t('admin.dashboard.deletedComments')" :value="stats.deleted_comments + stats.hard_deleted_comments" :icon="Trash2" color="#787c7e" />
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <h2 class="section-title">{{ t('admin.dashboard.chartsTitle') || 'Data Visualization' }}</h2>

        <div v-if="chartLoading" class="loading-container">
          <div class="loading-spinner"></div>
          <span>{{ t('common.loading') }}</span>
        </div>

        <div v-else class="charts-grid">
          <!-- 图表1: 帖子&评论状态分布 -->
          <div class="chart-card">
            <h3 class="chart-title">{{ t('admin.chart.statusDistribution') || 'Post & Comment Status' }}</h3>
            <v-chart class="chart" :option="statusPieOption" autoresize />
          </div>

          <!-- 图表2: 用户构成 -->
          <div class="chart-card">
            <h3 class="chart-title">{{ t('admin.chart.userComposition') || 'User Composition' }}</h3>
            <v-chart class="chart" :option="userPieOption" autoresize />
          </div>

          <!-- 图表3: 操作趋势 -->
          <div class="chart-card">
            <h3 class="chart-title">{{ t('admin.chart.operationTrend') || 'Operation Trend (30d)' }}</h3>
            <v-chart class="chart" :option="trendBarOption" autoresize />
          </div>

          <!-- 图表4: 操作类型统计 -->
          <div class="chart-card">
            <h3 class="chart-title">{{ t('admin.chart.actionStats') || 'Action Statistics' }}</h3>
            <v-chart class="chart" :option="actionBarOption" autoresize />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
}

.page-header { margin-bottom: 28px; }
.page-title {
  font-size: 22px; font-weight: 700; color: var(--text-primary); margin: 0 0 4px;
}
.page-desc { font-size: 14px; color: var(--text-secondary); margin: 0; }

.loading-container {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 60px 0; gap: 12px; color: var(--text-secondary);
}
.loading-spinner {
  width: 32px; height: 32px;
  border: 3px solid var(--border-color-light); border-top-color: #ff4500;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.stats-section { margin-bottom: 28px; }
.section-title {
  font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0 0 16px;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.charts-section { margin-top: 8px; }
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.chart-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color-light);
  border-radius: 12px;
  padding: 20px;
  min-height: 340px;
  display: flex;
  flex-direction: column;
}
.chart-title {
  font-size: 14px; font-weight: 600; color: var(--text-primary);
  margin: 0 0 12px;
}
.chart { flex: 1; min-height: 280px; }

@media (max-width: 900px) {
  .charts-grid { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }
}
</style>
