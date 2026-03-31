<template>
  <div class="create-post-container">
    <div class="create-post-card">
      <!-- 头部 -->
      <div class="card-header">
        <button class="back-btn" @click="goBack" :title="t('common.back')">
          <ArrowLeft :size="20" />
          <span>{{ t('common.back') }}</span>
        </button>
        <h2 class="title">{{ t('createPost.title') }}</h2>
      </div>

      <!-- 表单 -->
      <PostForm
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
import PostForm from '@/components/post/PostForm.vue'

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

const handleSubmit = (postId) => {
  console.log('[CreatePost] 发布成功，帖子 ID:', postId, '类型:', typeof postId)

  // 验证 ID 是否有效
  if (!postId || postId === 'undefined' || postId === 'null') {
    console.error('[CreatePost] 无效的帖子 ID:', postId)
    alert(t('createPost.publishSuccessButNoNav'))
    router.push('/')
    return
  }

  // 跳转到帖子详情页
  router.push(`/post/${postId}`)
}
</script>

<style scoped>
.create-post-container {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px 16px;
  background: #f6f7f8;
}

.create-post-card {
  width: 100%;
  max-width: 800px;
  background: #ffffff;
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
  .create-post-container {
    padding: 16px 8px;
  }

  .card-header {
    padding: 16px;
  }
}
</style>
