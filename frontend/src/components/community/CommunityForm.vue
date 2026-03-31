<template>
  <div class="community-form">

    <form @submit.prevent="onSubmit" class="form-body">
      <!-- 社区名称 -->
      <div class="form-group">
        <label class="form-label">
          <Hash :size="16" />
          <span>{{ t('communityForm.nameLabel') }}</span>
        </label>
        <input
          v-model="form.name"
          type="text"
          class="form-input"
          :placeholder="t('communityForm.namePlaceholder')"
          maxlength="50"
        />
        <div class="input-footer">
          <span class="hint">{{ t('communityForm.nameHint') }}</span>
          <span class="char-count">{{ form.name.length }}/50</span>
        </div>
        <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
      </div>

      <!-- 社区描述 -->
      <div class="form-group">
        <label class="form-label">
          <FileText :size="16" />
          <span>{{ t('communityForm.descriptionLabel') }}</span>
        </label>
        <textarea
          v-model="form.description"
          class="form-textarea"
          :placeholder="t('communityForm.descriptionPlaceholder')"
          rows="4"
          maxlength="500"
        ></textarea>
        <div class="input-footer">
          <span class="hint">{{ t('communityForm.descriptionHint') }}</span>
          <span class="char-count">{{ form.description.length }}/500</span>
        </div>
        <span v-if="errors.description" class="error-message">{{ errors.description }}</span>
      </div>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <button
          type="button"
          class="btn btn-secondary"
          @click="handleCancel"
          :disabled="isSubmitting"
        >
          {{ t('communityForm.cancel') }}
        </button>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="isSubmitting || !isFormValid"
        >
          <Send :size="16" v-if="!isSubmitting" />
          <span v-if="isSubmitting">{{ isEdit ? t('communityForm.saving') : t('communityForm.creating') }}</span>
          <span v-else>{{ isEdit ? t('communityForm.saveChanges') : t('communityForm.createCommunity') }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Hash, FileText, Send } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { client } from '@/api/client'

const { t } = useI18n()

const props = defineProps({
  isEdit: {
    type: Boolean,
    default: false
  },
  initialData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['submit', 'cancel'])

// 表单数据
const form = reactive({
  name: props.initialData?.name || '',
  description: props.initialData?.description || ''
})

// 状态
const isSubmitting = ref(false)
const errors = ref({})

// 计算属性
const isFormValid = computed(() => {
  return form.name.trim().length >= 3 &&
         form.name.trim().length <= 50 &&
         form.description.trim().length >= 10
})

// 验证方法
const validateName = () => {
  if (!form.name.trim()) {
    errors.value.name = t('communityForm.nameRequired')
    return false
  }
  if (form.name.trim().length < 3) {
    errors.value.name = t('communityForm.nameMinLength')
    return false
  }
  if (form.name.trim().length > 50) {
    errors.value.name = t('communityForm.nameMaxLength')
    return false
  }
  // 只允许字母、数字、中文和下划线
  const nameRegex = /^[\u4e00-\u9fa5a-zA-Z0-9_]+$/
  if (!nameRegex.test(form.name.trim())) {
    errors.value.name = t('communityForm.nameInvalidChars')
    return false
  }
  delete errors.value.name
  return true
}

const validateDescription = () => {
  if (!form.description.trim()) {
    errors.value.description = t('communityForm.descriptionRequired')
    return false
  }
  if (form.description.trim().length < 10) {
    errors.value.description = t('communityForm.descriptionMinLength')
    return false
  }
  if (form.description.trim().length > 500) {
    errors.value.description = t('communityForm.descriptionMaxLength')
    return false
  }
  delete errors.value.description
  return true
}

// 提交表单
const onSubmit = async () => {
  console.log('[社区表单] 开始提交')

  // 验证
  const isNameValid = validateName()
  const isDescValid = validateDescription()

  if (!isNameValid || !isDescValid) {
    console.log('[社区表单] 验证失败')
    return
  }

  isSubmitting.value = true

  try {
    const response = await client.POST('/v1/communities/', {
      body: {
        name: form.name.trim(),
        description: form.description.trim()
      }
    })

    if (response.data) {
      console.log('[社区表单] 创建成功, ID:', response.data.id)
      emit('submit', response.data)
    }
  } catch (error) {
    console.error('[社区表单] 创建失败:', error)
    // 错误已由 API 拦截器处理
  } finally {
    isSubmitting.value = false
  }
}

// 取消
const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.community-form {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #1c1c1c;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #878a8c;
  margin: 0;
}

.form-body {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
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

.form-input,
.form-textarea {
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

.form-input:focus,
.form-textarea:focus {
  border-color: #0079d3;
  background: #fff;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #878a8c;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
  line-height: 1.6;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
}

.hint {
  font-size: 12px;
  color: #878a8c;
}

.char-count {
  font-size: 12px;
  color: #878a8c;
}

.error-message {
  display: block;
  margin-top: 6px;
  color: #ff4500;
  font-size: 12px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
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

  .form-actions {
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
