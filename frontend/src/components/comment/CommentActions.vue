<template>
  <div class="comment-actions">
    <el-button
      text
      size="small"
      @click="isReplying ? $emit('cancel-reply') : $emit('reply')"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="action-icon">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      <span>{{ isReplying ? t('comment.cancel') : t('comment.reply') }}</span>
    </el-button>

    <!-- 整合的展开/收起按钮 -->
    <Transition name="expand-toggle" mode="out-in">
      <button
        v-if="comment.reply_count > 0"
        key="toggle"
        class="expand-toggle-btn"
        :class="{
          'is-expanded': isExpanded,
          'is-loading': repliesLoading
        }"
        @click="$emit('toggle-collapse')"
        :disabled="repliesLoading"
      >
        <!-- 细线条箭头图标 -->
        <span class="toggle-icon">
          <svg
            v-if="!repliesLoading"
            width="10"
            height="10"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="9 18 15 12 9 6"/>
          </svg>
          <el-icon v-else class="loading-spinner"><Loading /></el-icon>
        </span>
        
        <!-- 文字说明 -->
        <span class="toggle-text">
          {{ repliesLoading ? t('comment.loading') : (isExpanded ? t('comment.collapse') : t('comment.repliesCount', { count: comment.reply_count })) }}
        </span>
      </button>
    </Transition>

    <template v-if="canEdit">
      <el-button
        text
        size="small"
        @click="$emit('edit')"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="action-icon">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
        <span>{{ t('comment.edit') }}</span>
      </el-button>
    </template>

    <template v-if="canDelete">
      <el-button
        text
        size="small"
        class="delete-btn"
        @click="handleDelete"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="action-icon">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
        <span>{{ t('comment.delete') }}</span>
      </el-button>
    </template>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

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
  },
  isExpanded: {
    type: Boolean,
    default: false
  },
  repliesLoading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['reply', 'cancel-reply', 'edit', 'delete', 'load-more', 'toggle-collapse'])

const handleDelete = () => {
  ElMessageBox.confirm(
    t('comment.confirmDeleteMessage'),
    t('comment.confirmDeleteTitle'),
    {
      confirmButtonText: t('comment.confirmDeleteBtn'),
      cancelButtonText: t('comment.cancel'),
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
  gap: 16px;
  flex-wrap: wrap;
  margin-left: 44px;
  margin-top: 8px;
}

.comment-actions .el-button {
  padding: 4px 0;
  font-size: 12px;
  color: #999;
  background: transparent;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.comment-actions .el-button:hover {
  color: #333;
  background: transparent;
}

/* 操作图标样式 */
.action-icon {
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.comment-actions .el-button:hover .action-icon {
  opacity: 1;
}

.delete-btn:hover {
  color: #ff4500 !important;
}

/* 整合的展开/收起按钮 - 轻量级设计 */
.expand-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: #999;
  font-size: 12px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;
  user-select: none;
}

.expand-toggle-btn:hover:not(:disabled) {
  color: #333;
}

.expand-toggle-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.expand-toggle-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

/* 箭头图标 */
.toggle-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

/* 展开时箭头旋转90度（向右变为向下） */
.expand-toggle-btn.is-expanded .toggle-icon {
  transform: rotate(90deg);
}

/* 加载状态 */
.expand-toggle-btn.is-loading {
  color: #999;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 按钮切换动画 */
.expand-toggle-enter-active,
.expand-toggle-leave-active {
  transition: all 0.2s ease;
}

.expand-toggle-enter-from {
  opacity: 0;
  transform: translateX(-5px);
}

.expand-toggle-leave-to {
  opacity: 0;
  transform: translateX(5px);
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
