<template>
  <div class="comment-content">
    <!-- 左侧内容区 -->
    <div class="comment-main">
      <!-- 头像 -->
      <img
        v-if="comment.author_avatar"
        :src="comment.author_avatar"
        class="comment-avatar comment-avatar-img"
        @error="handleAvatarError"
      />
      <div v-else class="comment-avatar">{{ avatarText }}</div>

      <!-- 评论内容 -->
      <div class="comment-body">
        <!-- 用户名和时间 -->
        <div class="comment-header">
          <span class="comment-author">{{ comment.author_name || t('comment.anonymousUser') }}</span>
          <span class="comment-time">{{ formattedTime }}</span>
          <span v-if="comment.is_edited" class="comment-edited">({{ t('comment.edited') }})</span>
        </div>

        <!-- 评论文本 -->
        <div v-if="isDeleted" class="comment-deleted">
          <el-text type="info">{{ t('comment.deleted') }}</el-text>
        </div>
        <div v-else-if="isEditing" class="comment-editing">
          <el-input
            v-model="editContent"
            type="textarea"
            :rows="3"
            :placeholder="t('comment.editPlaceholder')"
            @keydown.ctrl.enter="saveEdit"
          />
          <div class="edit-actions">
            <el-button size="small" @click="$emit('cancel')">{{ t('comment.cancel') }}</el-button>
            <el-button type="primary" size="small" @click="saveEdit" :loading="saving">
              {{ t('comment.save') }}
            </el-button>
          </div>
        </div>
        <div v-else class="comment-text markdown-content" v-html="renderedContent"></div>
      </div>
    </div>

    <!-- 右侧投票按钮 -->
    <div v-if="!isDeleted" class="comment-vote-section">
      <VoteButton
        :comment-id="comment.id"
        :initial-upvotes="comment.upvotes || 0"
        :initial-downvotes="comment.downvotes || 0"
        :initial-score="comment.score || 0"
        @vote-changed="$emit('vote-changed', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { marked } from 'marked'
import { ElMessage } from 'element-plus'
import VoteButton from './VoteButton.vue'

const { t } = useI18n()

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  isDeleted: {
    type: Boolean,
    default: false
  },
  isEditing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit-save', 'cancel', 'vote-changed'])

const editContent = ref(props.comment.content || '')
const saving = ref(false)

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true
})

// 渲染 Markdown
const renderedContent = computed(() => {
  if (!props.comment.content) return ''
  try {
    return marked(props.comment.content)
  } catch (error) {
    console.error('Markdown 渲染错误:', error)
    return props.comment.content
  }
})

// 头像文字
const avatarText = computed(() => {
  const name = props.comment.author_name || 'U'
  return name.charAt(0).toUpperCase()
})

// 格式化时间
const formattedTime = computed(() => {
  if (!props.comment.created_at) return ''
  const date = new Date(props.comment.created_at)
  const now = new Date()
  const diff = (now - date) / 1000

  if (diff < 60) return t('common.justNow')
  if (diff < 3600) return t('common.minutesAgo', { n: Math.floor(diff / 60) })
  if (diff < 86400) return t('common.hoursAgo', { n: Math.floor(diff / 3600) })
  if (diff < 604800) return t('common.daysAgo', { n: Math.floor(diff / 86400) })

  return date.toLocaleDateString()
})

// 保存编辑
const saveEdit = async () => {
  if (!editContent.value.trim()) {
    ElMessage.warning(t('comment.contentRequired'))
    return
  }

  saving.value = true
  try {
    await emit('edit-save', editContent.value)
  } finally {
    saving.value = false
  }
}

// 头像加载失败处理
const handleAvatarError = (event) => {
  // 图片加载失败时隐藏img元素，会自动显示首字母头像
  event.target.style.display = 'none'
}
</script>

<style scoped>
.comment-content {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.comment-main {
  display: flex;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.comment-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

/* 子评论头像缩小 */
.level-1 .comment-avatar,
.level-2 .comment-avatar,
.level-3 .comment-avatar,
.level-4 .comment-avatar,
.level-5 .comment-avatar {
  width: 24px;
  height: 24px;
  font-size: 12px;
}

.comment-avatar-img {
  background: transparent;
  object-fit: cover;
  border: 1px solid #edeff1;
}

.comment-body {
  flex: 1;
  min-width: 0; /* 防止内容溢出 */
}

.comment-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

.comment-author {
  font-weight: 600;
  color: #1c1c1c;
  font-size: 14px;
}

.comment-time {
  color: #999999;
  font-size: 12px;
}

.comment-edited {
  color: #999999;
  font-size: 12px;
  font-style: italic;
}

.comment-text {
  font-size: 14px;
  line-height: 1.6;
  color: #1c1c1c;
  word-break: break-word;
  margin-top: 8px;
  margin-bottom: 8px;
}

.comment-deleted {
  color: #878a8c;
  font-style: italic;
}

.comment-editing {
  margin-top: 4px;
}

.edit-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  justify-content: flex-end;
}

.comment-vote-section {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  padding-top: 4px;
}

/* Markdown 样式 */
.markdown-content :deep(p) {
  margin: 0 0 8px 0;
}

.markdown-content :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-content :deep(code) {
  background: #f6f7f8;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background: #f6f7f8;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 8px 0;
}

.markdown-content :deep(pre code) {
  background: transparent;
  padding: 0;
}

.markdown-content :deep(blockquote) {
  border-left: 3px solid #0079d3;
  padding-left: 12px;
  margin: 8px 0;
  color: #878a8c;
}

.markdown-content :deep(a) {
  color: #0079d3;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}
</style>
