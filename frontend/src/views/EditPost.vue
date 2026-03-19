<template>
  <div class="edit-post-container">
    <div class="edit-post-card">
      <!-- Header -->
      <div class="card-header">
        <button class="back-btn" @click="goBack" title="返回">
          <ArrowLeft :size="20" />
          <span>返回</span>
        </button>
        <h2 class="title">编辑帖子</h2>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <!-- Form -->
      <PostForm
        v-else-if="postData"
        :initial-data="postData"
        :is-edit-mode="true"
        @submit="handleSubmit"
        @cancel="goBack"
      />

      <!-- Error state -->
      <div v-else class="error-state">
        <p>帖子不存在或无法加载</p>
        <button class="btn btn-primary" @click="goBack">返回</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from 'lucide-vue-next'
import { client } from '@/api/client'
import PostForm from '@/components/post/PostForm.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const postData = ref(null)
const loading = ref(true)

const loadPost = async () => {
  const postId = parseInt(route.params.id)
  if (isNaN(postId)) {
    loading.value = false
    return
  }

  loading.value = true
  try {
    const response = await client.GET('/v1/posts/{post_id}', {
      params: { path: { post_id: postId } }
    })
    if (response.data) {
      postData.value = response.data
    }
  } catch (error) {
    console.error('Failed to load post:', error)
    ElMessage.error('加载帖子失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push(`/post/${route.params.id}`)
}

const handleSubmit = async (formData) => {
  try {
    await client.PATCH('/v1/posts/{post_id}', {
      params: { path: { post_id: parseInt(route.params.id) } },
      body: {
        title: formData.title,
        content: formData.content,
        community_id: formData.community_id,
        attachment_ids: formData.attachment_ids || []
      }
    })
    ElMessage.success('编辑成功')
    router.push(`/post/${route.params.id}`)
  } catch (error) {
    console.error('Update failed:', error)
    ElMessage.error('更新失败')
  }
}

onMounted(() => {
  loadPost()
})
</script>

<style scoped>
.edit-post-container {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px 16px;
  background: #f6f7f8;
}

.edit-post-card {
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

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 24px;
  gap: 16px;
  color: #878a8c;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #edeff1;
  border-top-color: #0079d3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn {
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: #0079d3;
  color: #fff;
}

.btn-primary:hover {
  background: #0060a0;
}

@media (max-width: 639px) {
  .edit-post-container {
    padding: 16px 8px;
  }

  .card-header {
    padding: 16px;
  }
}
</style>
