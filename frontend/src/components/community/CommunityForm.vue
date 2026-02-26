<template>
  <div class="community-form">

    <form @submit.prevent="onSubmit" class="form-body">
      <!-- 社区名称 -->
      <div class="form-group">
        <label class="form-label">
          <Hash :size="16" />
          <span>社区名称</span>
        </label>
        <input
          v-model="form.name"
          type="text"
          class="form-input"
          placeholder="输入社区名称..."
          maxlength="50"
        />
        <div class="input-footer">
          <span class="hint">社区名称将作为 URL 的一部分，创建后不可修改</span>
          <span class="char-count">{{ form.name.length }}/50</span>
        </div>
        <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
      </div>

      <!-- 社区描述 -->
      <div class="form-group">
        <label class="form-label">
          <FileText :size="16" />
          <span>社区描述</span>
        </label>
        <textarea
          v-model="form.description"
          class="form-textarea"
          placeholder="描述这个社区的宗旨和内容..."
          rows="4"
          maxlength="500"
        ></textarea>
        <div class="input-footer">
          <span class="hint">简明扼要地告诉用户这个社区是关于什么的</span>
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
          取消
        </button>
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="isSubmitting || !isFormValid"
        >
          <Send :size="16" v-if="!isSubmitting" />
          <span v-if="isSubmitting">{{ isEdit ? '保存中...' : '创建中...' }}</span>
          <span v-else>{{ isEdit ? '保存修改' : '创建社区' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Hash, FileText, Send } from 'lucide-vue-next'
import { client } from '@/api/client'

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
    errors.value.name = '社区名称不能为空'
    return false
  }
  if (form.name.trim().length < 3) {
    errors.value.name = '社区名称至少需要 3 个字符'
    return false
  }
  if (form.name.trim().length > 50) {
    errors.value.name = '社区名称不能超过 50 个字符'
    return false
  }
  // 只允许字母、数字、中文和下划线
  const nameRegex = /^[\u4e00-\u9fa5a-zA-Z0-9_]+$/
  if (!nameRegex.test(form.name.trim())) {
    errors.value.name = '社区名称只能包含中文、字母、数字和下划线'
    return false
  }
  delete errors.value.name
  return true
}

const validateDescription = () => {
  if (!form.description.trim()) {
    errors.value.description = '社区描述不能为空'
    return false
  }
  if (form.description.trim().length < 10) {
    errors.value.description = '社区描述至少需要 10 个字符'
    return false
  }
  if (form.description.trim().length > 500) {
    errors.value.description = '社区描述不能超过 500 个字符'
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
