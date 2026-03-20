<template>
  <div class="reply-editor-wrapper">
    <!-- 现代化胶囊输入框 - 左右布局 -->
    <div class="pill-editor">
      <!-- 回复前缀标签 -->
      <span class="reply-prefix">
        <span class="reply-label">回复</span>
        <span class="reply-author">@{{ parentComment.author_name }}</span>
      </span>
      
      <!-- 输入区域 -->
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
          @keydown.esc="handleCancel"
          class="pill-textarea"
        />
      </div>
      
      <!-- 内嵌发送按钮 -->
      <button 
        class="send-btn" 
        :class="{ 'send-btn-active': isValid }"
        :disabled="!isValid"
        @click="handleSubmit"
        title="发送"
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
import { ref, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  postId: {
    type: Number,
    required: true
  },
  parentComment: {
    type: Object,
    required: true
  },
  placeholder: {
    type: String,
    default: '写下你的回复...'
  },
  minLength: {
    type: Number,
    default: 1
  },
  maxLength: {
    type: Number,
    default: 1000
  },
  autoFocus: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['submit', 'cancel'])

const content = ref('')
const inputRef = ref(null)

const isValid = computed(() =>
  content.value.length >= props.minLength &&
  content.value.length <= props.maxLength &&
  content.value.trim().length > 0
)

// 自动聚焦
if (props.autoFocus) {
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const handleSubmit = () => {
  if (!isValid.value) {
    if (content.value.length < props.minLength) {
      ElMessage.warning(`回复内容至少需要 ${props.minLength} 个字符`)
    } else {
      ElMessage.warning(`回复内容不能超过 ${props.maxLength} 个字符`)
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
</script>

<style scoped>
.reply-editor-wrapper {
  margin-top: 8px;
}

/* 现代化胶囊编辑器 - 整体化设计 */
.pill-editor {
  display: flex;
  align-items: center;
  gap: 0;
  background: #f0f2f5;
  border-radius: 24px;
  padding: 6px 6px 6px 14px;
  transition: all 0.2s ease;
}

.pill-editor:focus-within {
  background: #e8eaed;
  box-shadow: 0 0 0 2px rgba(0, 136, 254, 0.15);
}

/* 回复前缀标签 - 左侧 */
.reply-prefix {
  display: flex;
  align-items: center;
  gap: 4px;
  padding-right: 12px;
  border-right: 1px solid #dcdde0;
  margin-right: 10px;
  flex-shrink: 0;
  white-space: nowrap;
}

.reply-label {
  color: #8b8b8b;
  font-size: 13px;
  font-weight: 500;
}

.reply-author {
  font-size: 13px;
  font-weight: 600;
  color: #5a8dee;
}

/* 输入框容器 */
.pill-input-wrapper {
  flex: 1;
  min-width: 0;
}

.pill-input-wrapper :deep(.el-textarea__inner) {
  border: none;
  background: transparent;
  resize: none;
  font-size: 14px;
  line-height: 24px;
  padding: 0;
  min-height: 24px !important;
  max-height: 120px;
  /* 垂直居中关键 */
  display: flex;
  align-items: center;
}

.pill-input-wrapper :deep(.el-textarea__inner)::placeholder {
  color: #9ca3af;
  font-size: 14px;
}

.pill-input-wrapper :deep(.el-textarea__inner):focus {
  box-shadow: none;
}

/* 隐藏 textarea 边框 */
.pill-input-wrapper :deep(.el-textarea) {
  display: block;
}

.pill-input-wrapper :deep(.el-textarea__inner) {
  outline: none;
}

/* 修复 textarea 内部垂直居中 */
.pill-input-wrapper :deep(.el-textarea) {
  line-height: normal;
}

.pill-input-wrapper :deep(.el-textarea__inner) {
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
}

/* 内嵌发送按钮 */
.send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: #e5e5e5;
  border-radius: 50%;
  color: #a0a0a0;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  margin-left: 8px;
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
  color: #fff;
}

.send-btn-active:hover:not(:disabled) {
  background: #0077ee;
  color: #fff;
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
    padding: 5px 5px 5px 12px;
  }
  
  .reply-prefix {
    padding-right: 8px;
    margin-right: 8px;
  }
  
  .reply-label,
  .reply-author {
    font-size: 12px;
  }
  
  .send-btn {
    width: 32px;
    height: 32px;
    margin-left: 6px;
  }
  
  .send-icon {
    width: 16px;
    height: 16px;
  }
}
</style>
