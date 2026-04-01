<template>
  <div class="create-community-container">
    <div class="create-community-card">
      <!-- 头部 -->
      <div class="card-header">
        <button class="back-btn" @click="goBack" :title="t('common.back')">
          <ArrowLeft :size="20" />
          <span>{{ t('common.back') }}</span>
        </button>
        <h2 class="title">{{ t('createCommunity.title') }}</h2>
      </div>

      <!-- 表单 -->
      <CommunityForm
        @submit="handleSubmit"
        @cancel="goBack"
      />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowLeft } from 'lucide-vue-next'
import CommunityForm from '@/components/community/CommunityForm.vue'

const router = useRouter()
const { t } = useI18n()

const goBack = () => {
  // 如果有历史记录，返回上一页；否则返回首页
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

const handleSubmit = (community) => {
  console.log('[CreateCommunity] 创建成功, ID:', community.id, '类型:', typeof community)

  // 验证 ID 是否有效
  if (!community || !community.id) {
    console.error('[CreateCommunity] 无效的社区数据:', community)
    alert(t('createCommunity.createSuccessButNoNav'))
    router.push('/my-communities')
    return
  }

  // 跳转到我的社区页面
  router.push('/my-communities')
}
</script>

<style scoped>
.create-community-container {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px 16px;
  background: #f6f7f8;
}

.create-community-card {
  width: 100%;
  max-width: 600px;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #edeff1;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #f6f7f8;
  color: #1c1c1c;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #edeff1;
}

.title {
  font-size: 20px;
  font-weight: 600;
  color: #1c1c1c;
  margin: 0;
}

/* 响应式 */
@media (max-width: 639px) {
  .create-community-container {
    padding: 16px 8px;
  }

  .card-header {
    padding: 16px;
  }
}
</style>
