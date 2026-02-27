<template>
  <div class="reply-editor-wrapper">
    <!-- 引用被回复的评论 -->
    <div class="reply-quote">
      <span class="reply-label">回复</span>
      <span class="reply-author">{{ parentComment.author_name }}</span>
      <span class="reply-content-preview">{{ contentPreview }}</span>
    </div>

    <div class="reply-editor">
      <el-input
        ref="inputRef"
        v-model="content"
        type="textarea"
        :rows="3"
        :placeholder="placeholder"
        :maxlength="maxLength"
        @keydown.ctrl.enter="handleSubmit"
        @keydown.esc="handleCancel"
      />
    </div>

    <div class="reply-actions">
      <el-button
        type="primary"
        size="small"
        :disabled="!isValid"
        @click="handleSubmit"
      >
        发表回复
      </el-button>
      <el-button size="small" @click="handleCancel">
        取消
      </el-button>
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
  content.value.length <= props.maxLength
)

const contentPreview = computed(() => {
  const text = props.parentComment.content || ''
  return text.length > 30 ? text.substring(0, 30) + '...' : text
})

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
  margin-top: 12px;
  padding: 12px;
  background: #f6f7f8;
  border-radius: 8px;
}

.reply-quote {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 13px;
}

.reply-label {
  color: #878a8c;
}

.reply-author {
  font-weight: 600;
  color: #0079d3;
}

.reply-content-preview {
  color: #878a8c;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

.reply-editor :deep(.el-textarea__inner) {
  border-radius: 6px;
  resize: vertical;
  font-size: 14px;
}

.reply-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  justify-content: flex-end;
}

@media (max-width: 639px) {
  .reply-content-preview {
    max-width: 150px;
  }

  .reply-actions .el-button {
    font-size: 13px;
  }
}
</style>
