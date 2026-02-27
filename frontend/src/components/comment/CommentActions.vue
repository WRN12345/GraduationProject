<template>
  <div class="comment-actions">
    <el-button
      text
      size="small"
      :icon="isReplying ? ChevronUp : MessageCircle"
      @click="$emit('reply')"
    >
      {{ isReplying ? '取消回复' : '回复' }}
    </el-button>

    <span v-if="comment.reply_count > 0" class="reply-count">
      {{ comment.reply_count }} 条回复
    </span>

    <template v-if="canEdit">
      <el-button
        text
        size="small"
        :icon="Edit2"
        @click="$emit('edit')"
      >
        编辑
      </el-button>
    </template>

    <template v-if="canDelete">
      <el-button
        text
        size="small"
        :icon="Trash2"
        class="delete-btn"
        @click="handleDelete"
      >
        删除
      </el-button>
    </template>
  </div>
</template>

<script setup>
import { MessageCircle, ChevronUp, Edit2, Trash2 } from 'lucide-vue-next'
import { ElMessageBox } from 'element-plus'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  isReplying: {
    type: Boolean,
    default: false
  },
  canEdit: {
    type: Boolean,
    default: false
  },
  canDelete: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['reply', 'edit', 'delete', 'load-more'])

const handleDelete = () => {
  ElMessageBox.confirm(
    '确定要删除这条评论吗？删除后无法恢复。',
    '确认删除',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
      center: true,
      customClass: 'delete-confirm-box',
      draggable: false,
      closeOnClickModal: false,
      closeOnPressEscape: false
    }
  ).then(() => {
    emit('delete')
  }).catch(() => {
    // 用户取消
  })
}
</script>

<style scoped>
.comment-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  margin-left: 44px;
  margin-top: 8px;
}

.comment-actions .el-button {
  padding: 4px 8px;
  font-size: 13px;
  color: #878a8c;
}

.comment-actions .el-button:hover {
  color: #0079d3;
}

.delete-btn:hover {
  color: #ff4500 !important;
}

.reply-count {
  color: #878a8c;
  font-size: 13px;
  margin-left: 4px;
}

@media (max-width: 639px) {
  .comment-actions {
    margin-left: 0;
  }
}

/* 删除确认对话框增强样式 */
:deep(.delete-confirm-box) {
  width: 400px !important;
  max-width: 90vw !important;
  padding: 24px !important;
  border-radius: 12px !important;
  box-shadow: 0 12px 48px rgba(255, 69, 0, 0.25), 0 0 0 1px rgba(255, 69, 0, 0.1) !important;
}

:deep(.delete-confirm-box .el-message-box__header) {
  padding-bottom: 16px !important;
}

:deep(.delete-confirm-box .el-message-box__title) {
  font-size: 20px !important;
  font-weight: 600 !important;
  color: #1c1c1c !important;
}

:deep(.delete-confirm-box .el-message-box__content) {
  padding: 16px 0 !important;
  font-size: 15px !important;
  color: #878a8c !important;
  line-height: 1.6 !important;
}

:deep(.delete-confirm-box .el-message-box__btns) {
  padding-top: 16px !important;
  display: flex !important;
  justify-content: center !important;
  gap: 12px !important;
}

:deep(.delete-confirm-box .el-button--primary) {
  background-color: #ff4500 !important;
  border-color: #ff4500 !important;
  min-width: 100px !important;
  font-weight: 600 !important;
}

:deep(.delete-confirm-box .el-button--primary:hover) {
  background-color: #e03e00 !important;
  border-color: #e03e00 !important;
}

/* 增强遮罩层 */
:deep(.v-modal) {
  opacity: 0.6 !important;
  background: rgba(0, 0, 0, 0.5) !important;
  backdrop-filter: blur(2px) !important;
}
</style>
