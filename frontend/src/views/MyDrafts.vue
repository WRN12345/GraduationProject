<template>
  <div class="my-drafts-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>我的草稿箱</h1>
      <p class="subtitle">{{ total }} 篇草稿</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && drafts.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="drafts.length === 0" class="empty-state">
      <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
      </svg>
      <h3>还没有草稿</h3>
      <p>在创建帖子时，你可以随时保存为草稿</p>
      <button class="btn-primary" @click="goToCreatePost">创建新帖子</button>
    </div>

    <!-- 草稿列表 -->
    <div v-else class="drafts-list">
      <!-- 单个草稿卡片 -->
      <div
        v-for="draft in drafts"
        :key="draft.id"
        class="draft-card"
      >
        <!-- 社区信息 -->
        <div class="draft-header">
          <span class="community-icon">📝</span>
          <span class="community-name" v-if="draft.community">
            {{ draft.community.name }}
          </span>
          <span class="community-name no-community" v-else>
            未选择社区
          </span>
          <span class="meta-info">
            · 最后编辑 {{ formatTime(draft.updated_at) }}
          </span>
        </div>

        <!-- 标题 -->
        <h3 class="draft-title" v-if="draft.title">
          {{ draft.title }}
        </h3>
        <h3 class="draft-title no-title" v-else>
          无标题
        </h3>

        <!-- 内容预览 -->
        <div class="draft-preview" v-if="draft.content">
          {{ draft.content.substring(0, 200) }}{{ draft.content.length > 200 ? '...' : '' }}
        </div>
        <div class="draft-preview no-content" v-else>
          暂无内容
        </div>

        <!-- 底部操作区 -->
        <div class="draft-footer">
          <span class="draft-time">
            创建于 {{ formatTime(draft.created_at) }}
          </span>
          <div class="draft-actions">
            <button class="btn-action btn-edit" @click="editDraft(draft)">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              继续编辑
            </button>
            <button class="btn-action btn-publish" @click="publishDraft(draft)">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
              发布
            </button>
            <button class="btn-action btn-delete" @click="confirmDelete(draft)">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
              删除
            </button>
          </div>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore && !loading" class="load-more">
        <button class="btn-load-more" @click="loadMore" :disabled="loadingMore">
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </button>
      </div>

      <div v-if="loading && drafts.length > 0" class="loading-more">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="showDeleteDialog" class="dialog-overlay" @click.self="showDeleteDialog = false">
      <div class="dialog-card">
        <h3>确认删除</h3>
        <p>确定要删除这篇草稿吗？此操作不可撤销。</p>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="showDeleteDialog = false">取消</button>
          <button class="btn-confirm-delete" @click="handleDelete" :disabled="deleting">
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { client } from '@/api/client'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 响应式数据
const drafts = ref([])
const total = ref(0)
const skip = ref(0)
const limit = ref(20)
const hasMore = ref(false)
const loading = ref(false)
const loadingMore = ref(false)
const showDeleteDialog = ref(false)
const deleting = ref(false)
const pendingDeleteDraft = ref(null)

// 格式化时间
const formatTime = (dateString) => {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  const now = new Date()
  const diff = (now - date) / 1000

  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  if (diff < 604800) return `${Math.floor(diff / 86400)} 天前`

  return date.toLocaleDateString('zh-CN')
}

// 获取草稿列表
const fetchDrafts = async () => {
  loading.value = true
  try {
    const response = await client.GET('/v1/drafts', {
      params: {
        query: {
          skip: skip.value,
          limit: limit.value
        }
      }
    })

    if (response.error) {
      throw new Error(response.error.message || '获取草稿失败')
    }

    drafts.value = response.data.items
    total.value = response.data.total
    hasMore.value = response.data.has_more
  } catch (error) {
    console.error('获取草稿失败:', error)
    ElMessage.error('获取草稿失败')
  } finally {
    loading.value = false
  }
}

// 加载更多
const loadMore = async () => {
  loadingMore.value = true
  try {
    skip.value += limit.value

    const response = await client.GET('/v1/drafts', {
      params: {
        query: {
          skip: skip.value,
          limit: limit.value
        }
      }
    })

    if (response.error) {
      throw new Error(response.error.message || '加载更多失败')
    }

    drafts.value.push(...response.data.items)
    hasMore.value = response.data.has_more
  } catch (error) {
    console.error('加载更多失败:', error)
    ElMessage.error('加载更多失败')
    skip.value -= limit.value
  } finally {
    loadingMore.value = false
  }
}

// 继续编辑草稿 - 跳转到创建帖子页面，携带草稿数据
const editDraft = (draft) => {
  router.push({
    path: '/create-post',
    query: { draft_id: draft.id }
  })
}

// 发布草稿 - 跳转到创建帖子页面，携带草稿数据并标记为发布模式
const publishDraft = (draft) => {
  router.push({
    path: '/create-post',
    query: { draft_id: draft.id, publish: 'true' }
  })
}

// 确认删除
const confirmDelete = (draft) => {
  pendingDeleteDraft.value = draft
  showDeleteDialog.value = true
}

// 执行删除
const handleDelete = async () => {
  if (!pendingDeleteDraft.value) return

  deleting.value = true
  try {
    const response = await client.DELETE('/v1/drafts/{draft_id}', {
      params: {
        path: { draft_id: pendingDeleteDraft.value.id }
      }
    })

    if (response.error) {
      throw new Error(response.error.message || '删除失败')
    }

    // 从列表中移除
    drafts.value = drafts.value.filter(d => d.id !== pendingDeleteDraft.value.id)
    total.value -= 1
    ElMessage.success('草稿已删除')
  } catch (error) {
    console.error('删除草稿失败:', error)
    ElMessage.error('删除草稿失败')
  } finally {
    deleting.value = false
    showDeleteDialog.value = false
    pendingDeleteDraft.value = null
  }
}

// 跳转到创建帖子
const goToCreatePost = () => {
  router.push('/create-post')
}

// 页面挂载时获取数据
onMounted(() => {
  fetchDrafts()
})
</script>

<style scoped>
.my-drafts-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 16px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1c1c1c;
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 14px;
  color: #7c7c7c;
  margin: 0;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 0;
  color: #7c7c7c;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #edeff1;
  border-top-color: #0079d3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 0;
  color: #7c7c7c;
}

.empty-state svg {
  color: #d4d4d4;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1c1c1c;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 14px;
  margin: 0 0 20px 0;
}

.btn-primary {
  padding: 10px 24px;
  background: #0079d3;
  color: #fff;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #0062b1;
}

/* 草稿卡片 */
.draft-card {
  background: #ffffff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  transition: border-color 0.2s;
}

.draft-card:hover {
  border-color: #e2e2e2;
}

.draft-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #7c7c7c;
  margin-bottom: 8px;
}

.community-icon {
  font-size: 14px;
}

.community-name {
  font-weight: 600;
  color: #1c1c1c;
}

.community-name.no-community {
  color: #999;
  font-style: italic;
}

.meta-info {
  color: #999;
}

.draft-title {
  font-size: 16px;
  font-weight: 600;
  color: #1c1c1c;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.draft-title.no-title {
  color: #999;
  font-style: italic;
}

.draft-preview {
  font-size: 14px;
  color: #4a4a4a;
  line-height: 1.5;
  margin-bottom: 12px;
  white-space: pre-wrap;
  word-break: break-word;
}

.draft-preview.no-content {
  color: #999;
  font-style: italic;
}

/* 底部操作区 */
.draft-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid #f6f7f8;
}

.draft-time {
  font-size: 12px;
  color: #999;
}

.draft-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: none;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit {
  background: #f0f7ff;
  color: #0079d3;
}

.btn-edit:hover {
  background: #e0efff;
}

.btn-publish {
  background: #0079d3;
  color: #fff;
}

.btn-publish:hover {
  background: #0062b1;
}

.btn-delete {
  background: #fff0f0;
  color: #ea4335;
}

.btn-delete:hover {
  background: #ffe0e0;
}

/* 加载更多 */
.load-more {
  text-align: center;
  padding: 20px 0;
}

.btn-load-more {
  padding: 10px 24px;
  background: #f6f7f8;
  color: #1c1c1c;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-load-more:hover {
  background: #edeff1;
}

.btn-load-more:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-more {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  color: #7c7c7c;
}

/* 删除确认对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.dialog-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
}

.dialog-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1c1c1c;
  margin: 0 0 12px 0;
}

.dialog-card p {
  font-size: 14px;
  color: #7c7c7c;
  margin: 0 0 20px 0;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  padding: 8px 20px;
  background: #f6f7f8;
  color: #1c1c1c;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel:hover {
  background: #edeff1;
}

.btn-confirm-delete {
  padding: 8px 20px;
  background: #ea4335;
  color: #fff;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-confirm-delete:hover {
  background: #d33426;
}

.btn-confirm-delete:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
