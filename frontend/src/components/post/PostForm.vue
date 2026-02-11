<template>
  <form @submit.prevent="onSubmit" class="post-form">
    <!-- 草稿恢复提示 -->
    <div v-if="hasDraft && !draftRestored" class="draft-notice">
      <Info :size="16" />
      <span>检测到未保存的草稿</span>
      <button type="button" class="draft-btn" @click="restoreDraft">
        恢复草稿
      </button>
      <button type="button" class="draft-btn draft-btn-discard" @click="discardDraft">
        放弃
      </button>
    </div>

    <div class="form-body">
      <!-- 社区选择器 -->
      <div class="form-group">
        <label class="form-label">
          <Users :size="16" />
          <span>选择社区</span>
        </label>
        <CommunitySelector
          v-model="form.community_id"
          :communities="communities"
          :loading="loadingCommunities"
        />
        <span v-if="errors.community_id" class="error-message">
          {{ errors.community_id }}
        </span>
      </div>

      <!-- 标题输入 -->
      <div class="form-group">
        <label class="form-label">
          <FileText :size="16" />
          <span>标题</span>
        </label>
        <input
          ref="titleInputRef"
          v-model="form.title"
          type="text"
          class="form-input"
          placeholder="给帖子起一个吸引人的标题..."
          maxlength="300"
          @blur="validateTitle"
        />
        <div class="input-footer">
          <span v-if="errors.title" class="error-message">
            {{ errors.title }}
          </span>
          <span class="char-count">{{ form.title.length }}/300</span>
        </div>
      </div>

      <!-- 内容编辑 -->
      <div class="form-group">
        <label class="form-label">
          <AlignLeft :size="16" />
          <span>内容</span>
        </label>
        <MarkdownEditor
          ref="markdownEditorRef"
          v-model="form.content"
        />
        <span v-if="errors.content" class="error-message">
          {{ errors.content }}
        </span>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="form-footer">
      <button
        type="button"
        class="btn btn-secondary"
        @click="handleCancel"
        :disabled="isSubmitting"
      >
        取消
      </button>
      <button
        type="submit"
        class="btn btn-primary"
        :disabled="isSubmitting || !isFormValid"
      >
        <Send :size="16" v-if="!isSubmitting" />
        <span v-if="isSubmitting">发布中...</span>
        <span v-else>发布帖子</span>
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Users, FileText, AlignLeft, Info, Send } from 'lucide-vue-next'
import { client } from '@/api/client'
import { useDraft } from '@/composables/useDraft'
import CommunitySelector from './CommunitySelector.vue'
import MarkdownEditor from './MarkdownEditor.vue'

const emit = defineEmits(['submit', 'cancel'])

// 表单数据
const form = reactive({
  community_id: null,
  title: '',
  content: ''
})

// 状态
const communities = ref([])
const loadingCommunities = ref(false)
const isSubmitting = ref(false)
const errors = ref({})
const titleInputRef = ref(null)
const markdownEditorRef = ref(null)

// 草稿功能
const { draft, hasDraft, loadDraft, saveDraft, clearDraft, startAutoSave, stopAutoSave } = useDraft()
const draftRestored = ref(false)

// 计算属性
const isFormValid = computed(() => {
  return form.community_id &&
         form.title.trim().length >= 5 &&
         form.title.trim().length <= 300 &&
         form.content.trim().length >= 10
})

// 验证方法
const validateTitle = () => {
  if (!form.title.trim()) {
    errors.value.title = '标题不能为空'
    return false
  }
  if (form.title.trim().length < 5) {
    errors.value.title = '标题至少需要 5 个字符'
    return false
  }
  if (form.title.trim().length > 300) {
    errors.value.title = '标题不能超过 300 个字符'
    return false
  }
  delete errors.value.title
  return true
}

const validateContent = () => {
  if (!form.content.trim()) {
    errors.value.content = '内容不能为空'
    return false
  }
  if (form.content.trim().length < 10) {
    errors.value.content = '内容至少需要 10 个字符'
    return false
  }
  delete errors.value.content
  return true
}

const validateCommunity = () => {
  if (!form.community_id) {
    errors.value.community_id = '请选择一个社区'
    return false
  }
  delete errors.value.community_id
  return true
}

// 加载社区列表
const loadCommunities = async () => {
  loadingCommunities.value = true
  try {
    const response = await client.GET('/v1/communities', {
      params: {
        query: {
          skip: 0,
          limit: 100
        }
      }
    })
    if (response.data) {
      communities.value = response.data
      console.log('[社区] 加载成功，数量:', communities.value.length)
    }
  } catch (error) {
    console.error('[社区] 加载失败:', error)
  } finally {
    loadingCommunities.value = false
  }
}

// 恢复草稿
const restoreDraft = () => {
  if (draft.value) {
    form.community_id = draft.value.community_id
    form.title = draft.value.title
    form.content = draft.value.content
    draftRestored.value = true
    console.log('[草稿] 已恢复')
  }
}

// 放弃草稿
const discardDraft = () => {
  clearDraft()
  draftRestored.value = true
}

// 提交表单
const onSubmit = async () => {
  console.log('[表单] 开始提交')

  // 验证
  const isTitleValid = validateTitle()
  const isContentValid = validateContent()
  const isCommunityValid = validateCommunity()

  if (!isTitleValid || !isContentValid || !isCommunityValid) {
    console.log('[表单] 验证失败')
    return
  }

  isSubmitting.value = true

  try {
    const response = await client.POST('/v1/posts', {
      body: {
        title: form.title.trim(),
        content: form.content.trim(),
        community_id: form.community_id
      }
    })

    if (response.data) {
      console.log('[表单] 发布成功, ID:', response.data.id)
      // 清除草稿
      clearDraft()
      // 通知父组件
      emit('submit', response.data.id)
    }
  } catch (error) {
    console.error('[表单] 发布失败:', error)
    // 错误已由 API 拦截器处理
  } finally {
    isSubmitting.value = false
  }
}

// 取消
const handleCancel = () => {
  // 如果有内容，询问是否保存草稿
  if (form.title || form.content) {
    if (confirm('是否保存草稿？')) {
      saveDraft(form)
    }
  }
  emit('cancel')
}

// 生命周期
onMounted(() => {
  console.log('[表单] 组件挂载')
  // 加载社区列表
  loadCommunities()
  // 检查草稿
  loadDraft()
  // 启动自动保存
  startAutoSave(form)
  // 自动聚焦标题输入框
  setTimeout(() => {
    titleInputRef.value?.focus()
  }, 100)
})

onUnmounted(() => {
  console.log('[表单] 组件卸载')
  stopAutoSave()
})
</script>

<style scoped>
.post-form {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.draft-notice {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff8e1;
  border: 1px solid #ffd700;
  border-radius: 8px;
  margin-bottom: 16px;
  color: #f57c00;
  font-size: 14px;
}

.draft-btn {
  padding: 4px 12px;
  background: #f57c00;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: opacity 0.2s;
}

.draft-btn:hover {
  opacity: 0.9;
}

.draft-btn-discard {
  background: #edeff1;
  color: #878a8c;
}

.form-body {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #1c1c1c;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  border: 2px solid #edeff1;
  border-radius: 8px;
  color: #1c1c1c;
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
  font-family: inherit;
}

.form-input:focus {
  border-color: #0079d3;
  background: #fff;
}

.form-input::placeholder {
  color: #878a8c;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
}

.error-message {
  color: #ff4500;
  font-size: 12px;
}

.char-count {
  font-size: 12px;
  color: #878a8c;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #edeff1;
  background: #fafafa;
  border-radius: 0 0 12px 12px;
}

.btn {
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
  border: none;
}

.btn-secondary {
  background: #f6f7f8;
  color: #1c1c1c;
}

.btn-secondary:hover:not(:disabled) {
  background: #edeff1;
}

.btn-primary {
  background: #0079d3;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #0060a0;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式 */
@media (max-width: 639px) {
  .form-body {
    padding: 16px;
  }

  .form-footer {
    padding: 12px 16px;
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .draft-notice {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .draft-btn {
    width: 100%;
  }
}
</style>
