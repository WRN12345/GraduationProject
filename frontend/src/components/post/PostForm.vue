<template>
  <form @submit.prevent="onSubmit" class="post-form">
    <!-- 草稿恢复提示 -->
    <div v-if="!isEditMode && hasDraft && !draftRestored" class="draft-notice">
      <Info :size="16" />
      <span>{{ t('postForm.draftDetected') }}</span>
      <button type="button" class="draft-btn" @click="restoreDraft">
        {{ t('postForm.restoreDraft') }}
      </button>
      <button type="button" class="draft-btn draft-btn-discard" @click="discardDraft">
        {{ t('postForm.discard') }}
      </button>
    </div>

    <div class="form-body">
      <!-- 社区选择器 -->
      <div class="form-group">
        <label class="form-label">
          <Users :size="16" />
          <span>{{ t('postForm.selectCommunity') }}</span>
        </label>
        <CommunitySelector
          v-model="form.community_id"
          :communities="communities"
          :loading="loadingCommunities"
          :disabled="isEditMode"
        />
        <span v-if="errors.community_id" class="error-message">
          {{ errors.community_id }}
        </span>
      </div>

      <!-- 标题输入 -->
      <div class="form-group">
        <label class="form-label">
          <FileText :size="16" />
          <span>{{ t('postForm.title') }}</span>
        </label>
        <input
          ref="titleInputRef"
          v-model="form.title"
          type="text"
          class="form-input"
          :placeholder="t('postForm.titlePlaceholder')"
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
          <span>{{ t('postForm.content') }}</span>
        </label>
        <MarkdownEditor
          ref="markdownEditorRef"
          v-model="form.content"
        />
        <span v-if="errors.content" class="error-message">
          {{ errors.content }}
        </span>
      </div>

      <!-- 附件上传 -->
      <div class="form-group">
        <label class="form-label">
          <Paperclip :size="16" />
          <span>{{ t('postForm.attachment') }}</span>
          <span class="label-hint">{{ t('postForm.optional') }}</span>
        </label>
        <FileUploader
          ref="fileUploaderRef"
          upload-type="mixed"
          :limit="10"
          :file-list="attachmentList"
          @update:fileList="handleFileListUpdate"
          @upload-progress="handleUploadProgress"
          @upload-success="handleUploadSuccess"
        />
        <div v-if="isUploading" class="uploading-status">
          <span class="upload-spinner"></span>
          {{ t('postForm.uploadingAttachment') }}
        </div>
        <div v-else-if="attachmentList.length > 0" class="attachment-summary">
          {{ t('postForm.selectedAttachments', { count: attachmentList.length }) }}
        </div>
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
        {{ t('postForm.cancel') }}
      </button>
      <div class="footer-right">
        <button
          v-if="!isEditMode"
          type="button"
          class="btn btn-draft"
          @click="handleSaveDraft"
          :disabled="isSavingDraft || (!form.title && !form.content)"
        >
          <Save :size="16" v-if="!isSavingDraft" />
          <span v-if="isSavingDraft">{{ t('postForm.saving') }}</span>
          <span v-else>{{ t('postForm.saveDraft') }}</span>
        </button>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="isSubmitting || !isFormValid"
        >
          <Send :size="16" v-if="!isSubmitting" />
          <span v-if="isSubmitting">{{ isEditMode ? t('postForm.updating') : t('postForm.publishing') }}</span>
          <span v-else>{{ isEditMode ? t('postForm.updatePost') : t('postForm.publishPost') }}</span>
        </button>
      </div>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Users, FileText, AlignLeft, Info, Send, Paperclip, Save } from 'lucide-vue-next'
import { client } from '@/api/client'
import { useDraft } from '@/composables/useDraft'
import { ElMessage } from 'element-plus'
import CommunitySelector from './CommunitySelector.vue'
import MarkdownEditor from './MarkdownEditor.vue'
import FileUploader from '@/components/upload/FileUploader.vue'

const route = useRoute()
const { t } = useI18n()
const emit = defineEmits(['submit', 'cancel'])

const props = defineProps({
  initialData: {
    type: Object,
    default: null
  },
  isEditMode: {
    type: Boolean,
    default: false
  }
})

// 表单数据
const form = reactive({
  community_id: null,
  title: '',
  content: ''
})

// 监听社区选择变化，自动加入社区
watch(() => form.community_id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    console.log('[表单] 选择社区:', newId)
    // 尝试加入社区（如果已经是成员，后端会返回 400）
    try {
      await client.POST('/v1/communities/{community_id}/join', {
        params: {
          path: { community_id: newId }
        }
      })
      console.log('[表单] 已加入社区')
    } catch (error) {
      // 忽略"已经是成员"错误
      console.log('[表单] 加入社区结果:', error?.message || '已加入或已是成员')
    }
  }
})

// 状态
const communities = ref([])
const loadingCommunities = ref(false)
const isSubmitting = ref(false)
const errors = ref({})
const titleInputRef = ref(null)
const markdownEditorRef = ref(null)
const fileUploaderRef = ref(null)
const attachmentList = ref([])
const isUploading = ref(false)

// 草稿功能
const { draft, hasDraft, loadDraft, saveDraft, clearDraft, startAutoSave, stopAutoSave, saveDraftToServer, updateDraftToServer, deleteDraftFromServer } = useDraft()
const draftRestored = ref(false)
const isSavingDraft = ref(false)
const currentDraftId = ref(null) // 当前编辑的服务端草稿ID

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
    errors.value.title = t('postForm.titleEmpty')
    return false
  }
  if (form.title.trim().length < 5) {
    errors.value.title = t('postForm.titleMinLength')
    return false
  }
  if (form.title.trim().length > 300) {
    errors.value.title = t('postForm.titleMaxLength')
    return false
  }
  delete errors.value.title
  return true
}

const validateContent = () => {
  if (!form.content.trim()) {
    errors.value.content = t('postForm.contentEmpty')
    return false
  }
  if (form.content.trim().length < 10) {
    errors.value.content = t('postForm.contentMinLength')
    return false
  }
  delete errors.value.content
  return true
}

const validateCommunity = () => {
  if (!form.community_id) {
    errors.value.community_id = t('postForm.communityRequired')
    return false
  }
  delete errors.value.community_id
  return true
}

// 加载社区列表
const loadCommunities = async () => {
  loadingCommunities.value = true
  try {
    const response = await client.GET('/v1/communities/', {
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

// 保存草稿到服务端
const handleSaveDraft = async () => {
  if (!form.title && !form.content) {
    ElMessage.warning(t('postForm.titleOrContentRequired'))
    return
  }

  isSavingDraft.value = true
  try {
    const draftData = {
      title: form.title || '',
      content: form.content || '',
      community_id: form.community_id || null,
      attachment_ids: attachmentList.value
        .filter(f => f.attachmentId)
        .map(f => f.attachmentId)
    }

    let result
    if (currentDraftId.value) {
      // 更新已有草稿
      result = await updateDraftToServer(currentDraftId.value, draftData)
    } else {
      // 创建新草稿
      result = await saveDraftToServer(draftData)
    }

    if (result.data) {
      currentDraftId.value = result.data.id
      clearDraft() // 清除本地草稿（已保存到服务端）
      ElMessage.success(t('postForm.draftSaved'))
    } else if (result.error) {
      ElMessage.error(t('postForm.saveDraftFailedWith', { error: result.error.message || '' }))
    }
  } catch (error) {
    console.error('[表单] 保存草稿失败:', error)
    ElMessage.error(t('postForm.saveDraftFailed'))
  } finally {
    isSavingDraft.value = false
  }
}

// 处理文件列表更新
const handleFileListUpdate = (files) => {
  attachmentList.value = files
  console.log('[附件] 文件列表更新:', files.map(f => ({ name: f.name, id: f.attachmentId })))
}

// 处理上传进度
const handleUploadProgress = () => {
  isUploading.value = true
}

// 处理上传成功
const handleUploadSuccess = () => {
  isUploading.value = false
}

// 提交表单
const onSubmit = async () => {
  console.log('[表单] 开始提交')

  // 检查是否有正在上传的文件
  if (isUploading.value) {
    console.log('[表单] 文件上传中，请稍候')
    alert(t('postForm.waitUploadComplete'))
    return
  }

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
    // 获取附件 ID 列表
    const attachmentIds = attachmentList.value
      .filter(f => f.attachmentId)
      .map(f => f.attachmentId)

    console.log('[表单] 附件 ID:', attachmentIds)

    const formData = {
      title: form.title.trim(),
      content: form.content.trim(),
      community_id: form.community_id,
      attachment_ids: attachmentIds
    }

    if (props.isEditMode) {
      // 编辑模式 - 发送更新事件
      emit('submit', formData)
    } else {
      // 创建模式 - 发布帖子（用户选择社区时已自动加入）
      const response = await client.POST('/v1/posts', {
        body: formData
      })

      if (response.data) {
        console.log('[表单] 发布成功, ID:', response.data.id, '完整数据:', response.data)
        // 清除本地草稿
        clearDraft()
        // 如果是从服务端草稿发布的，删除该草稿
        if (currentDraftId.value) {
          try {
            await deleteDraftFromServer(currentDraftId.value)
            console.log('[表单] 已删除服务端草稿:', currentDraftId.value)
          } catch (e) {
            console.warn('[表单] 删除服务端草稿失败:', e)
          }
        }
        // 通知父组件
        emit('submit', response.data.id)
      } else {
        console.error('[表单] 发布失败，没有返回数据')
        alert(t('postForm.publishFailed'))
      }
    }
  } catch (error) {
    console.error('[表单] 发布失败:', error)
    alert(t('postForm.publishFailedWith', { error: error?.message || '' }))
  } finally {
    isSubmitting.value = false
  }
}

// 取消
const handleCancel = async () => {
  // 如果有内容且不是编辑模式，询问是否保存草稿
  if (!props.isEditMode && (form.title || form.content)) {
    if (confirm(t('postForm.saveDraftConfirm'))) {
      await handleSaveDraft()
    }
  }
  emit('cancel')
}

// 加载服务端草稿数据
const loadServerDraft = async (draftId) => {
  try {
    const response = await client.GET('/v1/drafts/{draft_id}', {
      params: {
        path: { draft_id: draftId }
      }
    })

    if (response.data) {
      const draftData = response.data
      form.title = draftData.title || ''
      form.content = draftData.content || ''
      form.community_id = draftData.community_id || null
      currentDraftId.value = draftData.id
      draftRestored.value = true

      // 处理附件
      if (draftData.attachment_ids && draftData.attachment_ids.length > 0) {
        // 附件需要从ID列表恢复（如果有附件信息的话）
        console.log('[表单] 草稿附件 IDs:', draftData.attachment_ids)
      }

      console.log('[表单] 已加载服务端草稿:', draftData.id)
      return true
    }
  } catch (error) {
    console.error('[表单] 加载服务端草稿失败:', error)
  }
  return false
}

// 生命周期
onMounted(async () => {
  console.log('[表单] 组件挂载')
  // 加载社区列表
  loadCommunities()

  // 如果是编辑模式，填充数据
  if (props.isEditMode && props.initialData) {
    form.community_id = props.initialData.community_id
    form.title = props.initialData.title
    form.content = props.initialData.content
    // 处理附件
    if (props.initialData.attachments) {
      attachmentList.value = props.initialData.attachments.map(a => ({
        file: null,
        preview: a.file_url,
        attachmentId: a.id
      }))
    }
  } else {
    // 检查是否有服务端草稿ID（从草稿箱跳转过来）
    const draftId = route.query.draft_id
    if (draftId) {
      await loadServerDraft(parseInt(draftId))
    } else {
      // 检查本地草稿
      loadDraft()
      // 启动自动保存
      startAutoSave(form)
    }
  }

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
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid #edeff1;
  background: #fafafa;
  border-radius: 0 0 12px 12px;
}

.footer-right {
  display: flex;
  gap: 12px;
  align-items: center;
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

.btn-draft {
  background: #f0f7ff;
  color: #0079d3;
  border: 1px solid #0079d3;
}

.btn-draft:hover:not(:disabled) {
  background: #e0efff;
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

.attachment-summary {
  font-size: 12px;
  color: #0079d3;
  margin-top: 8px;
}

.uploading-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #0079d3;
  margin-top: 8px;
}

.upload-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #edeff1;
  border-top-color: #0079d3;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 639px) {
  .form-body {
    padding: 16px;
  }

  .form-footer {
    padding: 12px 16px;
    flex-direction: column;
    gap: 8px;
  }

  .footer-right {
    flex-direction: column;
    width: 100%;
    gap: 8px;
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
