<template>
  <div class="comment-editor-wrapper">
    <div class="comment-editor">
      <el-input
        v-model="content"
        type="textarea"
        :rows="4"
        :placeholder="placeholder"
        :maxlength="maxLength"
        show-word-limit
        @keydown.ctrl.enter="handleSubmit"
      />
    </div>
    <div class="editor-actions">
      <el-button
        type="primary"
        :disabled="!isValid"
        :loading="submitting"
        @click="handleSubmit"
      >
        发表评论
      </el-button>
      <el-button v-if="content" @click="handleCancel">
        取消
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  postId: {
    type: Number,
    required: true
  },
  placeholder: {
    type: String,
    default: '写下你的评论...'
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

const isValid = computed(() =>
  content.value.length >= props.minLength &&
  content.value.length <= props.maxLength
)

const handleSubmit = () => {
  if (!isValid.value) {
    if (content.value.length < props.minLength) {
      ElMessage.warning(`评论内容至少需要 ${props.minLength} 个字符`)
    } else {
      ElMessage.warning(`评论内容不能超过 ${props.maxLength} 个字符`)
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
.comment-editor-wrapper {
  margin-bottom: 24px;
}

.comment-editor {
  margin-bottom: 12px;
}

.comment-editor :deep(.el-textarea__inner) {
  border-radius: 8px;
  resize: vertical;
  font-size: 14px;
  line-height: 1.5;
}

.editor-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

@media (max-width: 639px) {
  .editor-actions {
    flex-direction: column;
  }

  .editor-actions .el-button {
    width: 100%;
  }
}
</style>
