<template>
  <div class="comment-editor-wrapper">
    <!-- 现代化胶囊输入框 -->
    <div class="pill-editor">
      <div class="pill-input-wrapper">
        <el-input
          ref="inputRef"
          v-model="content"
          type="textarea"
          :rows="1"
          :placeholder="placeholder"
          :maxlength="maxLength"
          autosize
          @keydown.ctrl.enter="handleSubmit"
          class="pill-textarea"
        />
      </div>
      
      <!-- 字数提示 -->
      <span v-if="content.length > 0" class="char-count">{{ content.length }}/{{ maxLength }}</span>
      
      <!-- 内嵌发送按钮 -->
      <button
        class="send-btn"
        :class="{ 'send-btn-active': isValid }"
        :disabled="!isValid"
        @click="handleSubmit"
        :title="t('comment.send')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="send-icon">
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

const { t } = useI18n()

const props = defineProps({
  postId: {
    type: Number,
    required: true
  },
  placeholder: {
    type: String,
    default: ''
  },
  minLength: {
    type: Number,
    default: 1
  },
  maxLength: {
    type: Number,
    default: 2000
  },
  autofocus: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const content = ref('')
const submitting = ref(false)
const inputRef = ref(null)

const isValid = computed(() =>
  content.value.length >= props.minLength &&
  content.value.length <= props.maxLength &&
  content.value.trim().length > 0
)

// 自动聚焦
watch(() => props.autofocus, (val) => {
  if (val) {
    nextTick(() => {
      inputRef.value?.focus()
    })
  }
}, { immediate: true })

const handleSubmit = () => {
  if (!isValid.value) {
    if (content.value.length < props.minLength) {
      ElMessage.warning(t('comment.minLengthWarning', { min: props.minLength }))
    } else {
      ElMessage.warning(t('comment.maxLengthWarning', { max: props.maxLength }))
    }
    return
  }

  emit('submit', content.value)
  content.value = ''
}

const handleCancel = () => {
  content.value = ''
  emit('cancel')
}

// 暴露聚焦方法供父组件调用
defineExpose({
  focus: () => inputRef.value?.focus()
})
</script>

<style scoped>
.comment-editor-wrapper {
  margin-bottom: 0;
}

/* 现代化胶囊编辑器 */
.pill-editor {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f8f9fa;
  border-radius: 24px;
  padding: 6px 6px 6px 18px;
  transition: all 0.2s ease;
}

.pill-editor:focus-within {
  background: #f0f2f5;
  box-shadow: 0 0 0 2px rgba(0, 136, 254, 0.1);
}

/* 输入框容器 */
.pill-input-wrapper {
  flex: 1;
  min-width: 0;
}

.pill-input-wrapper :deep(.el-textarea__inner) {
  border: none;
  outline: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background: transparent;
  resize: none;
  font-size: 14px;
  line-height: 24px;
  padding: 0 0 0 16px;
  min-height: 24px !important;
  max-height: 120px;
  /* 垂直居中关键 */
  display: flex;
  align-items: center;
  /* 取消聚焦蓝框 */
  box-shadow: none !important;
}

.pill-input-wrapper :deep(.el-textarea__inner)::placeholder {
  color: #9ca3af;
  font-size: 14px;
}

.pill-input-wrapper :deep(.el-textarea__inner):focus {
  box-shadow: none !important;
  outline: none !important;
}

/* 隐藏 textarea 边框 */
.pill-input-wrapper :deep(.el-textarea) {
  display: block;
  line-height: normal;
}

.pill-input-wrapper :deep(.el-textarea__inner) {
  outline: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  box-shadow: none !important;
}

/* 字数统计 */
.char-count {
  font-size: 12px;
  color: #a1a1aa;
  flex-shrink: 0;
}

/* 内嵌发送按钮 */
.send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border: none;
  background: #e5e5e5;
  border-radius: 50%;
  color: #a0a0a0;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: #d0d0d0;
  color: #707070;
}

.send-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* 激活状态 - 输入时变蓝 */
.send-btn-active {
  background: #0088fe;
  color: var(--text-inverse);
}

.send-btn-active:hover:not(:disabled) {
  background: #0077ee;
  color: var(--text-inverse);
}

.send-btn-active:disabled {
  background: #e5e5e5;
  color: #a0a0a0;
  opacity: 0.5;
}

.send-icon {
  transform: translateX(1px);
}

@media (max-width: 639px) {
  .pill-editor {
    padding: 5px 5px 5px 14px;
    gap: 8px;
  }
  
  .send-btn {
    width: 34px;
    height: 34px;
  }
  
  .send-icon {
    width: 16px;
    height: 16px;
  }
  
  .char-count {
    font-size: 11px;
  }
}
</style>
